import os
import re
import textwrap
from pathlib import Path

import mechanicalsoup
import pytest
from mkdocs.commands.build import build
from mkdocs.config.base import load_config


class _Browser(mechanicalsoup.StatefulBrowser):
    def __init__(self, url: str):
        super().__init__(soup_config={"features": "html.parser"}, raise_on_404=True)
        self.open(url)

    def links(self, text=None, *args, **kwargs):
        all_links = super().links(*args, **kwargs)
        if text is not None:
            all_links = [a for a in all_links if a.text.strip() == text]
        return all_links


def build_site(cfg: str, src_dir: os.PathLike, dest_dir: os.PathLike) -> None:
    cfg_prefix = f"""
        site_name: SiteName
        site_dir: {str(dest_dir)!r}
        plugins:
            - section-index
    """
    cfg = textwrap.dedent(cfg_prefix) + textwrap.dedent(cfg)

    docs_dir = Path(src_dir, "docs")
    docs_dir.mkdir()
    Path(docs_dir, "README.md").write_text("")

    for rel_path in re.findall(r"\b[^ ]+\.md$", cfg, flags=re.MULTILINE):
        path = Path(docs_dir, rel_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(f"@{rel_path}@")

    f = Path(src_dir, "mkdocs.yml")
    f.write_text(cfg)
    build(load_config(str(f)))


@pytest.mark.parametrize("use_directory_urls", [True, False])
@pytest.mark.parametrize(
    "theme,features",
    [
        ("readthedocs", []),
        ("material", []),
        ("material", ["navigation.tabs"]),
        ("material", ["navigation.sections"]),
    ],
)
def test_nav_basic(http_server, tmpdir, use_directory_urls, theme, features):
    cfg = f"""
        use_directory_urls: {use_directory_urls!r}
        theme:
            name: {theme!r}
            features: {features}
        nav:
            - SectionWithIndex1:
                - Sub1/index.md
                - Aaa: Sub1/aaa.md
            - SectionWithIndex2:
                - Sub2/home.md
                - Bbb: Sub1/bbb.md
            - SectionWithoutIndex1:
                - Ccc: Sub2/ccc.md
                - Ddd: Sub2/ddd.md
    """
    build_site(cfg=cfg, src_dir=tmpdir, dest_dir=http_server.directory)
    browser = _Browser(http_server.url)
    # import webbrowser; webbrowser.open(browser.get_url()); input("...")

    browser.follow_link(text="SectionWithIndex1")
    assert browser.get_current_page().find_all(text="@Sub1/index.md@")

    browser.follow_link(text="SectionWithIndex2")
    assert browser.get_current_page().find_all(text="@Sub2/home.md@")

    assert len(browser.links(text="SectionWithIndex2")) >= 1 + features.count("navigation.tabs")
    assert len(browser.links(text="SectionWithoutIndex1")) >= features.count("navigation.tabs")

    browser.follow_link(text="Bbb")
    assert browser.get_current_page().find_all(text="@Sub1/bbb.md@")


@pytest.mark.parametrize("use_directory_urls", [True, False])
@pytest.mark.parametrize(
    "theme,features",
    [
        ("material", []),
        ("material", ["navigation.tabs"]),
        ("material", ["navigation.sections"]),
    ],
)
def test_nav_nested_tabs(http_server, tmpdir, use_directory_urls, theme, features):
    cfg = f"""
        use_directory_urls: {use_directory_urls!r}
        theme:
            name: {theme!r}
            features: {features}
        nav:
            - TabWithoutIndex1:
                - SectionWithIndex1:
                    - Sub1/index.md
                    - Aaa: Sub1/aaa.md
                - SectionWithIndex2:
                    - Sub2/home.md
                    - Bbb: Sub1/bbb.md
            - TabWithoutIndex2:
                - SectionWithoutIndex1:
                    - Ccc: Sub2/ccc.md
                    - Ddd: Sub2/ddd.md
                - SectionWithoutIndex2:
                    - Eee: Sub2/eee.md
    """
    build_site(cfg=cfg, src_dir=tmpdir, dest_dir=http_server.directory)
    browser = _Browser(http_server.url)
    # import webbrowser; webbrowser.open(browser.get_url()); input("...")

    browser.follow_link(text="SectionWithIndex1")
    assert browser.get_current_page().find_all(text="@Sub1/index.md@")
    browser.follow_link(text="SectionWithIndex2")
    assert browser.get_current_page().find_all(text="@Sub2/home.md@")

    if "navigation.tabs" in features:
        browser.follow_link(text="TabWithoutIndex1")
        assert browser.get_current_page().find_all(text="@Sub1/index.md@")
    assert not browser.links(text="SectionWithoutIndex1")


@pytest.mark.parametrize("use_directory_urls", [True, False])
@pytest.mark.parametrize(
    "theme,features",
    [
        ("material", []),
        ("material", ["navigation.tabs"]),
        ("material", ["navigation.sections"]),
    ],
)
def test_nav_nested_tabs_2(http_server, tmpdir, use_directory_urls, theme, features):
    cfg = f"""
        use_directory_urls: {use_directory_urls!r}
        theme:
            name: {theme!r}
            features: {features}
        nav:
            - TabWithIndex1:
                - Sub1/index.md
                - SectionWithoutIndex1:
                    - Aaa: Sub1/aaa.md
    """
    build_site(cfg=cfg, src_dir=tmpdir, dest_dir=http_server.directory)
    browser = _Browser(http_server.url)
    # import webbrowser; webbrowser.open(browser.get_url()); input("...")

    browser.follow_link(text="TabWithIndex1")
    assert browser.get_current_page().find_all(text="@Sub1/index.md@")
