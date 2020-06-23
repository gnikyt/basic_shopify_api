import pytest
from .utils import local_server_session, generate_opts_and_sess
from basic_shopify_api import Client


@pytest.mark.usefixtures("local_server")
@local_server_session
def test_graphql_return(local_server):
    with Client(*generate_opts_and_sess()) as c:
        response = c.graphql("{ shop { name } }")
        assert isinstance(response.body, dict)
        assert response.body["shop"]["name"] == "Apple Computers"
        assert response.errors is None
