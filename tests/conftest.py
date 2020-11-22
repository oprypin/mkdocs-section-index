import logging

import pytest
import testfixtures


@pytest.fixture(autouse=True)
def cap_log():
    with testfixtures.LogCapture(
        "mkdocs.plugins.mkdocs_section_index",
        attributes=("levelname", "getMessage"),
        ensure_checks_above=logging.WARNING,
    ) as capture:
        yield capture
