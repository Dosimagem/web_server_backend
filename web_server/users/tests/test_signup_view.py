from http import HTTPStatus

import pytest
from pytest_django.asserts import assertRedirects, assertTemplateUsed, assertFormError, assertContains
from django.urls import reverse
from web_server.users.models import CostumUser as User


URL_SINUP = reverse('signup')


@pytest.fixture
def resp_get(client):
    return client.get(URL_SINUP)


@pytest.fixture
def response(client, user_form):
    return client.post(URL_SINUP, data=user_form)


@pytest.fixture
def response_fail_signup(client, user_form_wrong_password):
    return client.post(URL_SINUP, data=user_form_wrong_password)


def test_success_get_signup_page_status(resp_get):
    assert resp_get.status_code == HTTPStatus.OK


def test_success_get_signup_template_page(resp_get):
    assertTemplateUsed(resp_get, 'users/signup.html')


def test_successful_signup(response):
    '''
    After registration the user must be redirected to login
    '''
    url = reverse('login')
    assertRedirects(response, url, status_code=HTTPStatus.FOUND)
    assert User.objects.count() == 1


def test_failed_signup(response_fail_signup):
    '''
    When the password does not match in the registration,
    it must fail and return to the registration page
    '''
    assertTemplateUsed(response_fail_signup, 'users/signup.html')

    assertFormError(response_fail_signup, 'form', field='password2', errors=['The two password fields didn’t match.'])

    assert User.objects.count() == 0


def test_failed_signup_input_filled(response_fail_signup):
    '''
    When the password does not match in the registration,
    it must fail and return to the registration page, but the entry must be filled.
    '''
    form = response_fail_signup.context['form']

    for field in ['name', 'email', 'phone', 'role', 'institution']:
        assertContains(response_fail_signup, 'value="{}"'.format(form.data[field]))

    assert User.objects.count() == 0
