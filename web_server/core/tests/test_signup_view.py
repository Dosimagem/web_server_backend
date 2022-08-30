# from http import HTTPStatus

# import pytest
# from pytest_django.asserts import assertRedirects, assertTemplateUsed, assertFormError, assertContains
# from django.urls import reverse
# from django.contrib.auth import get_user_model

# User = get_user_model()


# URL_SINUP = reverse('core:signup')


# @pytest.fixture
# def resp_get(client):
#     return client.get(URL_SINUP)


# @pytest.fixture
# def resp_post(client, register_infos, db):
#     return client.post(URL_SINUP, data=register_infos)


# @pytest.fixture
# def response_fail_signup(client, user_wrong_signup, db):
#     return client.post(URL_SINUP, data=user_wrong_signup)


# def test_success_get_signup_page_status(resp_get):
#     assert resp_get.status_code == HTTPStatus.OK


# def test_success_get_signup_template_page(resp_get):
#     assertTemplateUsed(resp_get, 'registration/signup.html')


# @pytest.mark.parametrize(
#     'field',
#     ['name', 'email', 'phone', 'institution', 'role', 'password1', 'password1'],
# )
# def test_field_in_signup_template(resp_get, field):
#     assertContains(resp_get, f'name="{field}"')


# def test_successful_signup(resp_post):
#     '''
#     After registration the user must be redirected to login
#     '''
#     url = reverse('core:login')
#     assertRedirects(resp_post, url, status_code=HTTPStatus.FOUND)
#     assert User.objects.count() == 1


# def test_failed_signup(response_fail_signup):
#     '''
#     When the password does not match in the registration,
#     it must fail and return to the registration page
#     '''
#     assertTemplateUsed(response_fail_signup, 'registration/signup.html')

#     assertFormError(response_fail_signup, 'form', field='password2', errors=['The two password fields didn’t match.'])

#     assert User.objects.count() == 0


# def test_failed_signup_input_filled(response_fail_signup):
#     '''
#     When the password does not match in the registration,
#     it must fail and return to the registration page, but the entry must be filled.
#     '''

#     form = response_fail_signup.context['form']

#     for field in ['name', 'email', 'role', 'institution', 'phone']:
#         assertContains(response_fail_signup, 'value="{}"'.format(form.data[field]))

#     assert User.objects.count() == 0


# def test_failed_signup_same_email_twice(client, register_infos, db):
#     '''
#     Trying to register the same email twice is not possible.
#     '''

#     resp = client.post(URL_SINUP, data=register_infos)

#     assert User.objects.count() == 1

#     resp = client.post(URL_SINUP, data=register_infos)

#     assert User.objects.count() == 1

#     assertFormError(resp, 'form', field='email', errors=['User with this Email address already exists.'])
