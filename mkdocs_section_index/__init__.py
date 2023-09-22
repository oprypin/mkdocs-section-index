from __future__ import annotations

from mkdocs.structure.nav import Section
from mkdocs.structure.pages import Page

__version__ = "0.3.8"
__all__ = ["SectionPage"]


class SectionPage(Section, Page):  # type: ignore[misc]
    def __init__(self, title: str, file, config, children):
        Page.__init__(self, title=title, file=file, config=config)
        Section.__init__(self, title=title, children=children)
        self.is_section = self.is_page = True

    active = Page.active  # type: ignore

    def __repr__(self):
        result = Page.__repr__(self)
        if not result.startswith("Section"):
            result = "Section" + result
        return result

    def __eq__(self, other):
        return object.__eq__(self, other)

    def __ne__(self, other):
        return not (self == other)

    def __hash__(self):
        return object.__hash__(self)
