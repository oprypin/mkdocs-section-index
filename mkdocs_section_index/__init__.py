from typing import Sequence

from mkdocs.config import Config
from mkdocs.structure.files import File
from mkdocs.structure.nav import Section
from mkdocs.structure.pages import Page

__all__ = ["SectionPage"]


class SectionPage(Section, Page):
    def __init__(self, title: str, file: File, config: Config, children: Sequence):
        Page.__init__(self, title=title, file=file, config=config)
        Section.__init__(self, title=title, children=children)
        self.is_section = self.is_page = True

    def __repr__(self):
        return "Section" + Page.__repr__(self)
