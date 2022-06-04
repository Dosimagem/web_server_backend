import pytest
from pytest_django.asserts import assertRedirects, assertTemplateUsed
from web_server.users.models import User


URL_SINUP = "/accounts/signup/"


@pytest.fixture
def form_user(db):
    return {"username": "User",
            "phone": "(11)999111213",
            "email": "test@email.com",
            "institution": "Institution_A",
            "role": "Engineer",
            "password1": "123456!!!###",
            "password2": "123456!!!###"
            }


@pytest.fixture
def form_user_wrong(db):
    return {"username": "User",
            "phone": "(11)999111213",
            "email": "test@email.com",
            "institution": "Institution_A",
            "role": "Engineer",
            "password1": "123456!!!###",
            "password2": "123456!!!###++"
            }


@pytest.fixture
def response(client, form_user):
    return client.post(URL_SINUP, data=form_user)


@pytest.fixture
def response_fail_signup(client, form_user_wrong):
    return client.post(URL_SINUP, data=form_user_wrong)


def test_successful_signup(response):
    assertRedirects(response, '/', status_code=302)
    assert User.objects.count() == 1


def test_failed_signup(response_fail_signup):

    assert response_fail_signup.status_code == 200

    assertTemplateUsed(response_fail_signup, 'users/signup.html')

    assert User.objects.count() == 0


def test_success_get_signup_page(client):
    response = client.get(URL_SINUP)

    assertTemplateUsed(response, 'users/signup.html')
