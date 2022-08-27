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
