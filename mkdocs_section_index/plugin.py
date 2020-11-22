import collections
import logging

import mkdocs.utils
from jinja2 import Environment
from mkdocs.plugins import BasePlugin
from mkdocs.structure.nav import Navigation, Section
from mkdocs.structure.pages import Page

from . import SectionPage, rewrites

__all__ = ["SectionIndexPlugin"]

log = logging.getLogger(f"mkdocs.plugins.{__name__}")
log.addFilter(mkdocs.utils.warning_filter)


class SectionIndexPlugin(BasePlugin):
    def on_nav(self, nav: Navigation, config, files) -> Navigation:
        todo = collections.deque((nav.items,))
        while todo:
            items = todo.popleft()
            for i, section in enumerate(items):
                if not isinstance(section, Section) or not section.children:
                    continue
                todo.append(section.children)
                page = section.children[0]
                if not isinstance(page, Page):
                    continue
                assert not page.children
                if not page.title and page.url:
                    # The page becomes a section-page.
                    page.__class__ = SectionPage
                    page.is_section = page.is_page = True
                    page.title = section.title
                    # The page leaves the section but takes over children that used to be its peers.
                    section.children.pop(0)
                    page.children = section.children
                    for child in page.children:
                        child.parent = page
                    # The page replaces the section; the section will be garbage-collected.
                    items[i] = page
        return nav

    def on_env(self, env: Environment, config, files) -> Environment:
        env.loader = self._loader = rewrites.TemplateRewritingLoader(env.loader)
        return env

    def on_post_build(self, config):
        if not self._loader.found_supported_theme:
            log.warning(
                "section-index plugin couldn't detect a supported theme to adapt. "
                "It probably won't work as expected. "
                "See https://github.com/oprypin/mkdocs-section-index#theme-support"
            )
