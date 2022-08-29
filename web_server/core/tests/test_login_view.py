# from http import HTTPStatus

# from django.urls import reverse
# import pytest
# from pytest_django.asserts import assertContains, assertTemplateUsed


# @pytest.fixture
# def response(client):
#     return client.get(reverse('core:login'))


# def test_login_status(response):
#     assert response.status_code == HTTPStatus.OK


# def test_template_login(response):
#     assertTemplateUsed(response, 'registration/login.html')


# @pytest.mark.parametrize(
#     'field',
#     ['username', 'password'],
# )
# def test_field_in_signup_template(response, field):

#     assertContains(response, f'name="{field}"')


# def test_login_page_redirect(client, django_user_model):
#     '''
#     After login the user is redirect for profile
#     '''
#     user_form_login = dict(username='test@email.com', password='1234')

#     django_user_model.objects.create_user(email=user_form_login['username'],
#                                           password=user_form_login['password'])

#     resp = client.post(reverse('core:login'), data=user_form_login)

#     assert resp.status_code == HTTPStatus.FOUND
#     assert f'{resp.url}/' == f'{reverse("client:profile")}'


# def test_link_forget_password(response):

#     assertContains(response, '<a href="{}">'.format(reverse('core:password_reset')))
