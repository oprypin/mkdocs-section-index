import pathlib

import pytest
from mkdocs.config import load_config
from mkdocs.structure.files import get_files
from mkdocs.structure.nav import get_navigation

from mkdocs_section_index import SectionPage, plugin

example_dir = pathlib.Path(__file__).parent / ".." / "example"


@pytest.mark.parametrize("directory_urls", ["use_directory_urls", "no_directory_urls"])
@pytest.mark.parametrize("nav", ["explicit_nav", "derived_nav"])
def test_real_example_without_nav(golden, tmpdir, directory_urls, nav):
    config = dict(
        docs_dir=str(example_dir / "docs"),
        site_dir=tmpdir,
        use_directory_urls=(directory_urls == "use_directory_urls"),
        nav=load_config(str(example_dir / "mkdocs.yml"))["nav"] if nav == "explicit_nav" else None,
    )
    files = get_files(config)
    nav = get_navigation(files, config)
    nav = plugin.SectionIndexPlugin().on_nav(nav, config, files)

    assert len(nav.pages) == 5
    assert len(nav.items) == 3

    assert nav.items[1].is_page
    assert nav.items[1].file.name == "baz"
    assert not nav.items[1].is_section

    sec = nav.items[2]
    assert isinstance(sec, SectionPage)
    assert sec.is_section
    assert sec.is_page
    assert sec.title == "Borgs"
    assert sec.url in ("borgs/", "borgs/index.html")
    assert sec.file.name == "index"

    assert len(sec.children) == 2
    assert sec.children[0].is_page
    assert sec.children[0].file.name == "bar"
