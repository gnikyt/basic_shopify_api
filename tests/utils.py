import pytest
from functools import wraps
from multiprocessing import Process
from unittest.mock import patch, PropertyMock
from wsgiref.simple_server import make_server

def local_server_session(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        from unittest.mock import patch, PropertyMock
        with patch("basic_shopify_api.Session.base_url", new_callable=PropertyMock) as mock_base_url:
            mock_base_url.return_value = "http://localhost:8080"
            return func(*args, **kwargs)
    return wrapper

def local_server_app(environ, start_response):
    status = "200 OK"
    headers = [("Content-Type", "application/json")]
    start_response(status, headers, ['{"hey":"man"}'])
    return ['{}'.encode("utf-8")]


@pytest.fixture
def local_server():
    httpd = make_server("localhost", 8080, local_server_app)
    process = Process(
        target=httpd.serve_forever,
        daemon=True,
    )
    process.start()
    yield
    process.terminate()
    process.join()
