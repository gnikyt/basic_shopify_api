import pytest
from .utils import local_server_session
from basic_shopify_api import Client, Options, Session
from basic_shopify_api.constants import ACCESS_TOKEN_HEADER, DEFAULT_MODE, ALT_MODE


def generate_opts_and_sess(mode=DEFAULT_MODE):
    opts = Options()
    opts.mode = mode

    sess = Session("example.myshopify.com", "abc", "123")
    return (sess, opts)


def test_is_authable():
    with Client(*generate_opts_and_sess()) as c:
        assert c.is_authable("/admin/api/shop.json") is True
        assert c.is_authable("/oauth/access_token") is False


def test_is_versionable():
    with Client(*generate_opts_and_sess()) as c:
        assert c.is_versionable("/admin/api/shop.json") is True
        assert c.is_versionable("/oauth/access_scopes") is False


def test_version_path():
    with Client(*generate_opts_and_sess()) as c:
        assert c.version_path("/admin/api/shop.json") == "/admin/api/2020-04/shop.json"
        assert c.version_path("/admin/api/shop.json", True) == "/admin/api/2020-04/shop.json"


def test_build_headers():
    with Client(*generate_opts_and_sess(ALT_MODE)) as c:
        headers = c._build_headers({})
        assert headers[ACCESS_TOKEN_HEADER] == "123"

    with Client(*generate_opts_and_sess()) as c:
        headers = c._build_headers({})
        assert ACCESS_TOKEN_HEADER not in headers


def test_build_request():
    with Client(*generate_opts_and_sess()) as c:
        request = c._build_request(
            method="get",
            path="/admin/api/shop.json",
            params={"fields": "id"},
        )
        assert "params" in request
        assert "2020-04" in request["url"]

    with Client(*generate_opts_and_sess()) as c:
        request = c._build_request(
            method="post",
            path="/admin/api/shop.json",
            params={"fields": "id"},
        )
        assert "json" in request


def test_rest_extract_link():
    page_info = "eyJsYXN0X2lkIjo0MDkwMTQ0ODQ5OTgyLCJsYXN_0X3ZhbHVlIjoiPGh0bWw-PGh0bWw-MiBZZWFyIERWRCwgQmx1LVJheSwgU2F0ZWxsaXRlLCBhbmQgQ2FibGUgRnVsbCBDaXJjbGXihKIgMTAwJSBWYWx1ZSBCYWNrIFByb2R1Y3QgUHJvdGVjdGlvbiB8IDIgYW4gc3VyIGxlcyBsZWN0ZXVycyBEVkQgZXQgQmx1LXJheSBldCBwYXNzZXJlbGxlcyBtdWx0aW3DqWRpYXMgYXZlYyByZW1pc2Ugw6AgMTAwICUgQ2VyY2xlIENvbXBsZXQ8c3VwPk1DPFwvc3VwPjxcL2h0bWw-PFwvaHRtbD4iLCJkaXJlY3Rpb24iOiJuZXh0In0"
    with Client(*generate_opts_and_sess()) as c:
        result = c._rest_extract_link({
            "link": f"<https://example.myshopify.com/admin/api/unstable/products.json?page_info={page_info}>; rel=\"next\""
        })
        assert result.next == page_info
        assert result.prev is None


@pytest.mark.usefixtures("local_server")
@local_server_session
def test_moo(local_server):
    with Client(*generate_opts_and_sess()) as c:
        response = c.rest("get", "/admin/api/shop.json")
        assert isinstance(response.body, dict)
