import pytest
from rest_framework.test import APIClient


@pytest.fixture
def client_api():
    return APIClient()


HTTP_METHODS = {
    'get': APIClient().get,
    'post': APIClient().post,
    'put': APIClient().put,
    'patch': APIClient().patch,
    'delete': APIClient().delete
}


@pytest.fixture
def client_api_auth(client_api, user):
    client_api.credentials(HTTP_AUTHORIZATION='Bearer ' + user.auth_token.key)
    return client_api
