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


@pytest.fixture
def form_data_clinic_dosimetry(clinic_dosimetry_info, clinic_dosimetry_file):

    return {
         'calibration_id' : clinic_dosimetry_info['calibration'].uuid,
         'images': clinic_dosimetry_file['images']
    }
