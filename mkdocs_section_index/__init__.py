from __future__ import annotations

from mkdocs.config import Config
from mkdocs.structure.files import File
from mkdocs.structure.nav import Link, Section
from mkdocs.structure.pages import Page

__version__ = "0.3.5"
__all__ = ["SectionPage"]


class SectionPage(Section, Page):  # type: ignore[misc]
    def __init__(
        self, title: str, file: File, config: Config, children: list[Page | Section | Link]
    ):
        Page.__init__(self, title=title, file=file, config=config)
        Section.__init__(self, title=title, children=children)
        self.is_section = self.is_page = True

    active = Page.active  # type: ignore

    def __repr__(self):
        return "Section" + Page.__repr__(self)

    def __eq__(self, other):
        return object.__eq__(self, other)

    def __ne__(self, other):
        return not (self == other)

    def __hash__(self):
        return object.__hash__(self)
