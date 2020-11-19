import collections
import pathlib

import jinja2.loaders
import mkdocs.plugins
import mkdocs.structure.nav
import mkdocs.structure.pages


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
        env.loader = TemplateEditingLoader(env.loader)
        return env


class TemplateEditingLoader(jinja2.loaders.BaseLoader):
    def __init__(self, loader: jinja2.loaders.BaseLoader):
        self.loader = loader

    def get_source(self, environment: jinja2.environment.Environment, template: str):
        src, filename, uptodate = self.loader.get_source(environment, template)

        template = "/".join(jinja2.loaders.split_template_path(template))
        path = pathlib.Path(filename).as_posix()

        if path.endswith("/material/partials/nav-item.html"):
            src = transform_material_nav_template(src)

        return src, filename, uptodate


def transform_material_nav_template(src):
    lines = src.split("\n")
    for i, line in enumerate(lines):
        if line.endswith("{{ nav_item.title }}") and "href=" not in lines[i - 1]:
            lines[i] = (
                "{% if nav_item.url %}"
                '<a href="{{ nav_item.url | url }}"'
                ' class="{% if nav_item == page %} md-nav__link--active{% endif %}">'
                "{% endif %}"
                f"{line}"
                "{% if nav_item.url %}</a>{% endif %}"
            )
    return "\n".join(lines)
