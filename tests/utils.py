import pytest
import os
from functools import wraps
from multiprocessing import Process
from unittest.mock import patch, PropertyMock
from wsgiref.simple_server import make_server
from basic_shopify_api import Options, Session
from basic_shopify_api.constants import DEFAULT_MODE

server_host = "localhost"
server_port = 8080


def local_server_session(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        with patch("basic_shopify_api.Session.base_url", new_callable=PropertyMock) as mock_base_url:
            mock_base_url.return_value = f"http://{server_host}:{server_port}"
            return func(*args, **kwargs)
    return wrapper


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
    httpd = make_server(server_host, server_port, local_server_app)
    process = Process(target=httpd.serve_forever, daemon=True)
    process.start()
    yield
    process.terminate()
    process.join()


def generate_opts_and_sess(mode=DEFAULT_MODE):
    opts = Options()
    opts.mode = mode

    sess = Session("example.myshopify.com", "abc", "123")
    return (sess, opts)
