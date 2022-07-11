from http import HTTPStatus
from django.urls import reverse


def test_logout_redirect(client):
    response = client.get(reverse('core:logout'))

    assert response.status_code == HTTPStatus.FOUND
