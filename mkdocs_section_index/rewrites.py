import pathlib

import jinja2.environment
import jinja2.loaders


class TemplateEditingLoader(jinja2.loaders.BaseLoader):
    def __init__(self, loader: jinja2.loaders.BaseLoader):
        self.loader = loader

    def get_source(self, environment: jinja2.environment.Environment, template: str):
        src, filename, uptodate = self.loader.get_source(environment, template)
        path = pathlib.Path(filename).as_posix()

        if path.endswith("/material/partials/nav-item.html"):
            src = _transform_material_nav_template(src)

        return src, filename, uptodate


def _transform_material_nav_template(src):
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
