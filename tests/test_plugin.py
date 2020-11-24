import contextlib
import dataclasses
import pathlib

import pytest
from jinja2 import Environment, FileSystemLoader
from mkdocs.config import Config, load_config
from mkdocs.structure.files import File, get_files
from mkdocs.structure.nav import Navigation, get_navigation
from testfixtures import StringComparison

from mkdocs_section_index import SectionPage, plugin

example_dir = pathlib.Path(__file__).parent / ".." / "example"


@pytest.mark.parametrize("directory_urls", ["use_directory_urls", "no_directory_urls"])
@pytest.mark.parametrize("nav", ["explicit_nav", "derived_nav"])
def test_real_example(tmpdir, directory_urls, nav):
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

    assert nav.items[1].next_page == sec
    assert sec.children[1].parent == sec


@dataclasses.dataclass
class FakeFiles:
    config: Config

    def get_file_from_path(self, path):
        if ":" not in path:
            return File(
                path,
                src_dir=self.config.get("docs_dir", ""),
                dest_dir=self.config.get("site_dir", ""),
                use_directory_urls=self.config.get("use_directory_urls", True),
            )

    @classmethod
    def documentation_pages(cls):
        return []


@pytest.mark.golden_test("navs/*.yml")
def test_nav_repr(golden, tmpdir):
    for use_directory_urls in True, False:
        config = dict(nav=golden["input"], use_directory_urls=use_directory_urls)
        files = FakeFiles(config)
        nav = get_navigation(files, config)
        nav = plugin.SectionIndexPlugin().on_nav(nav, config, files)
        assert str(nav) == golden.out[use_directory_urls]


@contextlib.contextmanager
def template_test(directory):
    config = dict()
    files = FakeFiles(config)
    env = Environment(loader=FileSystemLoader(directory))
    env.filters["url"] = lambda s: s

    plg = plugin.SectionIndexPlugin()
    plg.on_nav(Navigation([], []), config, files)
    env = plg.on_env(env, config, files)

    yield env

    plg.on_post_build(config)


def test_build_material(tmpdir):
    directory = tmpdir.mkdir("material")
    directory.mkdir("partials").join("nav-item.html").write_text(
        "md-nav__icon\n{{ nav_item.title }}", encoding="utf-8"
    )
    with template_test(directory) as env:
        env.get_template("partials/nav-item.html")


def test_build_wrong_content(cap_log, tmpdir):
    directory = tmpdir.mkdir("material")
    directory.mkdir("partials").join("nav-item.html").write_text(
        "href=\n{{ nav_item.title }}", encoding="utf-8"
    )
    with template_test(directory) as env:
        env.get_template("partials/nav-item.html")
    cap_log.check(("WARNING", StringComparison("Failed to adapt.+nav-item.+")))


def test_build_wrong_file(cap_log, tmpdir):
    directory = tmpdir.mkdir("foo")
    directory.mkdir("partials").join("nav-item.html").write_text(
        "{{ nav_item.title }}", encoding="utf-8"
    )
    with template_test(directory) as env:
        env.get_template("partials/nav-item.html")
    cap_log.check(("WARNING", StringComparison(".+couldn't detect a supported theme.+")))
