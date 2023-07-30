import pytest
from .utils import generate_opts_and_sess, local_server_session, async_local_server_session
from fastshopifyapi import Client, AsyncClient


@pytest.mark.usefixtures("local_server")
@local_server_session
def test_graphql_return(local_server):
    with Client(*generate_opts_and_sess()) as c:
        response = c.graphql("{ shop { name } }")
        assert isinstance(response.body, dict)
        assert response.body["data"]["shop"]["name"] == "Apple Computers"
        assert response.errors is None


@pytest.mark.asyncio
@pytest.mark.usefixtures("local_server")
@async_local_server_session
async def test_graphql_async_return(local_server):
    async with AsyncClient(*generate_opts_and_sess()) as c:
        response = await c.graphql("{ shop { name } }")
        assert isinstance(response.body, dict)
        assert response.body["data"]["shop"]["name"] == "Apple Computers"
        assert response.errors is None
