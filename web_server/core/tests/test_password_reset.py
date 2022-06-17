from http import HTTPStatus

from pytest_django.asserts import assertTemplateUsed

from django.urls import reverse


def test_password_reset_status_code(client):
    resp = client.get(reverse('password_reset'))

    assert resp.status_code == HTTPStatus.OK


def test_password_reset_tamplete(client):
    resp = client.get(reverse('password_reset'))

    assertTemplateUsed(resp, 'registration/password_reset_form.html')
