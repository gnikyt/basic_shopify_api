import pytest
from http import HTTPStatus
from .utils import generate_opts_and_sess, local_server_session, async_local_server_session
from fastshopifyapi import Client, AsyncClient


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
        for i in range(2):
            c.options.time_store.append(c.session, c.options.deferrer.current_time())

        c.rest("get", "/admin/api/shop.json")
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
        for i in range(2):
            c.options.time_store.append(c.session, c.options.deferrer.current_time())
        c.options.cost_store.append(c.session, 100)

        c.graphql("{ shop { name } }")
        assert len(c.options.time_store.all(c.session)) == 1
        assert len(c.options.cost_store.all(c.session)) == 1


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


@pytest.mark.asyncio
@pytest.mark.usefixtures("local_server")
@async_local_server_session
async def test_async_rest_rate_limit():
    async with AsyncClient(*generate_opts_and_sess()) as c:
        for i in range(2):
            c.options.time_store.append(c.session, c.options.deferrer.current_time())

        await c.rest("get", "/admin/api/shop.json")
        assert len(c.options.time_store.all(c.session)) == 1


@pytest.mark.asyncio
@pytest.mark.usefixtures("local_server")
@async_local_server_session
async def test_async_graphql_cost_limit():
    async with AsyncClient(*generate_opts_and_sess()) as c:
        for i in range(2):
            c.options.time_store.append(c.session, c.options.deferrer.current_time())
        c.options.cost_store.append(c.session, 100)

        await c.graphql("{ shop { name } }")
        assert len(c.options.time_store.all(c.session)) == 1
        assert len(c.options.cost_store.all(c.session)) == 1
