import pytest
import os
from http import HTTPStatus
from multiprocessing import Process
from wsgiref.simple_server import make_server
from fastshopifyapi.constants import RETRY_HEADER


def local_server_app(environ, start_response):
    method = environ["REQUEST_METHOD"].lower()
    path = environ["PATH_INFO"].split("/")[-1]
    status = environ.get("HTTP_X_TEST_STATUS", f"{HTTPStatus.OK.value} {HTTPStatus.OK.description}")
    headers = [("Content-Type", "application/json")]
    fixture = environ.get("HTTP_X_TEST_FIXTURE", f"{method}_{path}")
    if "HTTP_X_TEST_RETRY" in environ:
        headers.append((RETRY_HEADER, environ["HTTP_X_TEST_RETRY"]))

    with open(os.path.dirname(__file__) + f"/fixtures/{fixture}") as fixture:
        data = fixture.read().encode("utf-8")

    start_response(status, headers)
    return [data]


@pytest.fixture
def local_server():
    httpd = make_server("localhost", 8080, local_server_app)
    process = Process(target=httpd.serve_forever, daemon=True)
    process.start()
    yield
    process.terminate()
    process.join()
