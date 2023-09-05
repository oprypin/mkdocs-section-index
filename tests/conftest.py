import functools
import http.server
import logging
import threading

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


@pytest.fixture(scope="session")
def http_server(tmp_path_factory):
    directory = tmp_path_factory.mktemp("http_server")
    httpd = http.server.HTTPServer(
        ("localhost", 0),
        functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(directory)),
    )
    t = threading.Thread(target=httpd.serve_forever)
    t.daemon = True
    t.start()
    httpd.directory = directory
    httpd.url = f"http://localhost:{httpd.server_port}/"
    return httpd
