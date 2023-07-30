import pytest
from json import JSONDecodeError
from fastshopifyapi import Client, AsyncClient
from .utils import generate_opts_and_sess, local_server_session, async_local_server_session


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
def test_rest_return(local_server):
    with Client(*generate_opts_and_sess()) as c:
        response = c.rest("get", "/admin/api/shop.json")
        assert isinstance(response.body, dict)
        assert response.body["shop"]["name"] == "Apple Computers"
        assert response.link.next is None
        assert response.link.prev is None
        assert response.errors is None


@pytest.mark.usefixtures("local_server")
@local_server_session
def test_rest_error_return(local_server):
    with Client(*generate_opts_and_sess()) as c:
        response = c.rest("get", "/admin/api/error.json")
        assert response.body is None
        assert response.errors == "Not found"

        response = c.rest("get", "/admin/api/errors.json")
        assert response.body is None
        assert response.errors == "Not found"

        response = c.rest("get", "/admin/api/decode_error.json")
        assert response.body is None
        assert isinstance(response.errors, JSONDecodeError)


@pytest.mark.asyncio
@pytest.mark.usefixtures("local_server")
@async_local_server_session
async def test_rest_async_return(local_server):
    async with AsyncClient(*generate_opts_and_sess()) as c:
        response = await c.rest("get", "/admin/api/shop.json")
        assert isinstance(response.body, dict)
        assert response.body["shop"]["name"] == "Apple Computers"
        assert response.link.next is None
        assert response.link.prev is None
        assert response.errors is None
