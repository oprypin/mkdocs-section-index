import pytest

from mkdocs_section_index import rewrites


@pytest.mark.golden_test("rewrites/material-nav-item-*.yml")
def test_rewrite_material_nav(golden):
    assert rewrites._transform_material_nav_template(golden["input"]) == golden.out["output"]
