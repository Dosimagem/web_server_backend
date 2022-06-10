from http import HTTPStatus

import pytest
from pytest_django.asserts import assertTemplateUsed, assertContains
from django.urls import reverse


@pytest.fixture
def logged_user(client, django_user_model):
    email, password = 'test@email.com', '1234'  # TODO: Extrair isso para umq fixture

    user = django_user_model.objects.create_user(email=email, password=password)

    client.force_login(user)

    return user


@pytest.fixture
def resp(client, logged_user):
    return client.get(reverse('profile'))


def test_profile_status_code(resp):
    assert resp.status_code == HTTPStatus.OK


def test_profile_template(resp):
    assertTemplateUsed(resp, 'users/profile.html')


def test_services_in_context(resp):
    '''
    Checks if requests are in HTML context
    '''
    assert 'solicitations' in resp.context.keys()


def test_profile_view_have_table_with_two_lines(resp):
    '''
    Need there are two rows in the table
    '''
    assertContains(resp, 'scope="row"', 2)
