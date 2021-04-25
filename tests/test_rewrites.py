import pytest

from mkdocs_section_index import rewrites


@pytest.mark.golden_test("rewrites/mkdocs-sitemap-*.yml")
def test_rewrite_mkdocs_sitemap(golden):
    assert rewrites._transform_mkdocs_sitemap_template(golden["input"]) == golden.out["output"]


@pytest.mark.golden_test("rewrites/readthedocs-base-*.yml")
def test_rewrite_readthedocs_base(golden):
    assert rewrites._transform_readthedocs_base_template(golden["input"]) == golden.out["output"]


@pytest.mark.golden_test("rewrites/material-nav-item-*.yml")
def test_rewrite_material_nav_item(golden):
    assert rewrites._transform_material_nav_item_template(golden["input"]) == golden.out["output"]


@pytest.mark.golden_test("rewrites/material-tabs-item-*.yml")
def test_rewrite_material_tabs_item(golden):
    assert rewrites._transform_material_tabs_item_template(golden["input"]) == golden.out["output"]
