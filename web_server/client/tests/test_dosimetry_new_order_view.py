from http import HTTPStatus

from django.shortcuts import resolve_url
from django.urls import reverse
from pytest_django.asserts import assertTemplateUsed, assertContains


def test_dosimetry_order_view_status_code(client, logged_user):
    resp = client.get(resolve_url('client:dosimetry_order'))

    assert resp.status_code == HTTPStatus.OK


def test_dosimetry_order_view_template(client, logged_user):
    resp = client.get(resolve_url('client:dosimetry_order'))

    assertTemplateUsed(resp, 'client/dosimetry_order.html')


def test_dosimetry_order_only_login_user(client):
    '''
    Client not login must be redirect for login view
    '''
    url = resolve_url('client:dosimetry_order')

    resp = client.get(url)

    assert resp.status_code == HTTPStatus.FOUND
    assert resp.url == f'{reverse("core:login")}?next={url}'


def test_dosimetry_order_labels(client, logged_user):

    resp = client.get(resolve_url('client:dosimetry_order'))

    assertContains(resp, 'Camera Factor')
    assertContains(resp, 'Radionuclide')
    assertContains(resp, 'Injected Activity')
    assertContains(resp, 'Injenction Time')
    assertContains(resp, 'Images')
