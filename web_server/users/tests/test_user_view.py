from http import HTTPStatus

import pytest
from pytest_django.asserts import assertRedirects, assertTemplateUsed
from django.urls import reverse
from web_server.users.models import CostumUser as User


URL_SINUP = reverse('signup')


@pytest.fixture
def response(client, user_form):
    return client.post(URL_SINUP, data=user_form)


@pytest.fixture
def response_fail_signup(client, user_form_wrong_password):
    return client.post(URL_SINUP, data=user_form_wrong_password)


def test_successful_signup(response):  # TODO: write comment
    url = reverse('index')
    assertRedirects(response, url, status_code=HTTPStatus.FOUND)
    assert User.objects.count() == 1


def test_failed_signup(response_fail_signup):  # TODO: write comment

    assert response_fail_signup.status_code == HTTPStatus.OK

    assertTemplateUsed(response_fail_signup, 'users/signup.html')

    assert User.objects.count() == 0


def test_success_get_signup_page(client):  # TODO: write comment

    response = client.get(URL_SINUP)

    assertTemplateUsed(response, 'users/signup.html')
