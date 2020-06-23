import pytest
import os
from multiprocessing import Process
from wsgiref.simple_server import make_server


def local_server_app(environ, start_response):
    method = environ["REQUEST_METHOD"].lower()
    path = environ["PATH_INFO"].split("/")[-1]
    status = "200 OK"
    headers = [("Content-Type", "application/json")]

    with open(os.path.dirname(__file__) + f"/fixtures/{method}_{path}") as fixture:
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
