from http import HTTPStatus

import pytest
from pytest_django.asserts import assertTemplateUsed, assertContains
from django.urls import reverse


@pytest.fixture
def resp(client, logged_user, orders_user):
    return client.get(reverse('client:profile'))


def test_profile_status_code(resp):
    assert resp.status_code == HTTPStatus.OK


def test_profile_template(resp):
    assertTemplateUsed(resp, 'profile/profile.html')


def test_services_in_context(resp):
    '''
    Checks if requests are in HTML context
    '''
    assert 'solicitations' in resp.context.keys()


def test_profile_view_have_table_with_four_lines(resp):
    '''
    Need there are two rows in the table
    '''
    assertContains(resp, 'scope="row"', 4)


def test_profile_view_have_order_names(resp):
    '''
    Need there are ordes name
    '''
    assertContains(resp, 'Dosimetria Clinica')
    assertContains(resp, 'Dosimetria Preclinica')
    assertContains(resp, 'Segmentação'.encode())
    assertContains(resp, 'Modelagem Computacional')


def test_profile_view_have_order_prices(resp):
    '''
    Need there are ordes name
    '''
    assertContains(resp, '3710.42')
    assertContains(resp, '2000.02')
    assertContains(resp, '2000.50')
    assertContains(resp, '12001.65')
