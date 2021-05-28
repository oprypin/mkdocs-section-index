import collections
import logging
import os

import mkdocs.utils
from jinja2 import Environment
from mkdocs.plugins import BasePlugin
from mkdocs.structure.nav import Navigation, Section
from mkdocs.structure.pages import Page

from . import SectionPage, rewrites

__all__ = ["SectionIndexPlugin"]

log = logging.getLogger(f"mkdocs.plugins.{__name__}")
log.addFilter(mkdocs.utils.warning_filter)


def move_second_before_first(first, second, before="previous_page", after="next_page"):
    """
    Move second element before first in a doubly linked list.
    """
    el_before_second = getattr(second, before)
    el_after_second = getattr(second, after)
    el_before_first = getattr(first, before)

    # now fix links from left to right
    if el_before_first:
        setattr(el_before_first, after, second)
    setattr(second, before, el_before_first)
    setattr(second, after, first)
    setattr(first, before, second)
    if el_before_second:
        setattr(el_before_second, after, el_after_second)
    if el_after_second:
        setattr(el_after_second, before, el_before_second)


class SectionIndexPlugin(BasePlugin):
    config_scheme = (("index_file", mkdocs.config.config_options.Type(str, default=None)),)

    def on_nav(self, nav: Navigation, config, files) -> Navigation:
        todo = collections.deque((nav.items,))
        while todo:
            items = todo.popleft()
            for i, section in enumerate(items):
                if not isinstance(section, Section) or not section.children:
                    continue
                todo.append(section.children)
                index_file = self.config["index_file"]
                if index_file is None:
                    page_index = 0
                    page = section.children[0]
                else:
                    for page_index, child in enumerate(section.children):
                        if os.path.basename(child.file.src_path) == index_file:
                            page = child
                            break
                    else:
                        continue
                if not isinstance(page, Page):
                    continue
                assert not page.children
                if not page.title and page.url:
                    # The page becomes a section-page.
                    page.__class__ = SectionPage
                    page.is_section = page.is_page = True
                    page.title = section.title
                    # The page leaves the section but takes over children that used to be its peers.
                    section.children.pop(page_index)
                    page.children = section.children
                    for child in page.children:
                        child.parent = page
                    # Correct order if changed
                    if page_index > 0:
                        move_second_before_first(page.children[0], page)
                    # The page replaces the section; the section will be garbage-collected.
                    items[i] = page

        self._nav = nav
        return nav

    def on_env(self, env: Environment, config, files) -> Environment:
        env.loader = self._loader = rewrites.TemplateRewritingLoader(env.loader)
        return env

    def on_page_context(self, context, page, config, nav):
        if nav != self._nav:
            self._nav = nav
            log.warning(
                "It seems that the effects of section-index plugin have been lost, because another MkDocs plugin re-wrote the nav! "
                "Re-order `plugins` in mkdocs.yml so that 'section-index' appears closer to the end."
            )

    def on_post_build(self, config):
        if not self._loader.found_supported_theme:
            log.warning(
                "section-index plugin couldn't detect a supported theme to adapt. "
                "It probably won't work as expected. "
                "See https://github.com/oprypin/mkdocs-section-index#theme-support"
            )
