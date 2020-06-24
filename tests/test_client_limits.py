import pytest
from http import HTTPStatus
from .utils import generate_opts_and_sess, local_server_session, async_local_server_session
from basic_shopify_api import Client, AsyncClient


@pytest.mark.usefixtures("local_server")
@local_server_session
def test_rest_retry():
    with Client(*generate_opts_and_sess()) as c:
        response = c.rest(
            method="get",
            path="/admin/shop.json",
            headers={"x-test-status": f"{HTTPStatus.BAD_GATEWAY.value} {HTTPStatus.BAD_GATEWAY.phrase}"},
        )
        assert 502 in response.status
        assert response.retries == c.options.max_retries


@pytest.mark.usefixtures("local_server")
@local_server_session
def test_rest_rate_limit():
    with Client(*generate_opts_and_sess()) as c:
        c.rest("get", "/admin/shop.json")
        assert len(c.options.time_store.all(c.session)) == 1

        c.rest("get", "/admin/shop.json")
        assert len(c.options.time_store.all(c.session)) == 2

        c.rest("get", "/admin/shop.json")
        assert len(c.options.time_store.all(c.session)) == 1


@pytest.mark.usefixtures("local_server")
@local_server_session
def test_graphql_retry():
    with Client(*generate_opts_and_sess()) as c:
        response = c.graphql(
            query="{ shop { name } }",
            headers={"x-test-status": f"{HTTPStatus.BAD_GATEWAY.value} {HTTPStatus.BAD_GATEWAY.phrase}"},
        )
        assert 502 in response.status
        assert response.retries == c.options.max_retries


@pytest.mark.usefixtures("local_server")
@local_server_session
def test_graphql_cost_limit():
    with Client(*generate_opts_and_sess()) as c:
        c.graphql("{ shop { name } }")
        c.graphql("{ shop { name } }")

    with Client(*generate_opts_and_sess()) as c:
        c.graphql(
            query="{ shop { name } }",
            headers={"x-test-fixture": "post_graphql_expensive.json"}
        )


@pytest.mark.usefixtures("local_server")
@local_server_session
def test_rest_retry_header():
    with Client(*generate_opts_and_sess()) as c:
        response = c.rest(
            method="get",
            path="/admin/shop.json",
            headers={
                "x-test-status": f"{HTTPStatus.BAD_GATEWAY.value} {HTTPStatus.BAD_GATEWAY.phrase}",
                "x-test-retry": "1.0",
            }
        )
        assert 502 in response.status
        assert response.retries == c.options.max_retries


@pytest.mark.asyncio
@pytest.mark.usefixtures("local_server")
@async_local_server_session
async def test_async_rest_retry():
    async with AsyncClient(*generate_opts_and_sess()) as c:
        response = await c.rest(
            method="get",
            path="/admin/shop.json",
            headers={"x-test-status": f"{HTTPStatus.BAD_GATEWAY.value} {HTTPStatus.BAD_GATEWAY.phrase}"},
        )
        assert 502 in response.status
        assert response.retries == c.options.max_retries
