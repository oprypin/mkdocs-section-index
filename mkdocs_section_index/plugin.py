import collections

import jinja2.environment
import mkdocs.plugins
import mkdocs.structure.nav
import mkdocs.structure.pages

from . import rewrites


class SectionIndexPlugin(mkdocs.plugins.BasePlugin):
    def on_nav(
        self, nav: mkdocs.structure.nav.Navigation, config, files
    ) -> mkdocs.structure.nav.Navigation:
        todo = collections.deque((nav.items,))
        while todo:
            items = todo.popleft()
            for i, section in enumerate(items):
                if not isinstance(section, mkdocs.structure.nav.Section) or not section.children:
                    continue
                todo.append(section.children)
                page = section.children[0]
                if not isinstance(page, mkdocs.structure.pages.Page):
                    continue
                assert not page.children
                if not page.title and page.url:
                    items[i] = page
                    page.is_section = page.is_page = True
                    section.children.pop(0)
                    page.children = section.children
                    for child in page.children:
                        child.parent = page
                    page.title = section.title
        return nav

    def on_env(
        self, env: jinja2.environment.Environment, config, files
    ) -> jinja2.environment.Environment:
        env.loader = rewrites.TemplateEditingLoader(env.loader)
        return env
