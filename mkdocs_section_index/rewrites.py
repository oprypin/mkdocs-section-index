import pathlib
import textwrap
from typing import Optional, Tuple

import jinja2.environment
import jinja2.loaders


class TemplateRewritingLoader(jinja2.loaders.BaseLoader):
    def __init__(self, loader: jinja2.loaders.BaseLoader):
        self.loader = loader

    def get_source(
        self, environment: jinja2.environment.Environment, template: str
    ) -> Tuple[str, str, bool]:
        src, filename, uptodate = self.loader.get_source(environment, template)
        path = pathlib.Path(filename).as_posix()

        if path.endswith("/material/partials/nav-item.html"):
            src = _transform_material_nav_template(src)

        return src, filename, uptodate


def _transform_material_nav_template(src: str) -> str:
    repl = """\
        {% if nav_item.url %}
          <a href="{{ nav_item.url | url }}"{% if nav_item == page %}  class="md-nav__link--active"{% endif %}>
        {% endif %}
          [...]
        {% if nav_item.url %}</a>{% endif %}
    """
    lines = src.split("\n")
    for i, line in enumerate(lines):
        if line.endswith("{{ nav_item.title }}") and "href=" not in lines[i - 1]:
            lines[i] = _replace_line(lines[i], repl)
    return "\n".join(lines)


def _replace_line(line: str, wrapper: str, new_line: Optional[str] = None) -> str:
    leading_space = line[: -len(line.lstrip())]
    if new_line is None:
        new_line = line.lstrip()
    new_text = textwrap.dedent(wrapper.rstrip()).replace("[...]", new_line)
    return textwrap.indent(new_text, leading_space)
