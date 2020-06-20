import pytest
from basic_shopify_api import Client, Options, Session
from basic_shopify_api.constants import ACCESS_TOKEN_HEADER, DEFAULT_MODE, ALT_MODE

def generate_opts_and_sess(mode=DEFAULT_MODE):
  opts = Options()
  opts.mode = mode

  sess = Session("example.myshopify.com", "abc", "123")
  return (sess, opts)

def test_is_authable():
  with Client(*generate_opts_and_sess()) as c:
    assert c.is_authable("/admin/api/shop.json") == True
    assert c.is_authable("/oauth/access_token") == False

def test_is_versionable():
  with Client(*generate_opts_and_sess()) as c:
    assert c.is_versionable("/admin/api/shop.json") == True
    assert c.is_versionable("/oauth/access_scopes") == False

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