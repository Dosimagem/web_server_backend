from http import HTTPStatus

from django.urls import reverse


def test_profile_redirect_for_login_page_user_not_login(client):
    '''
    User not logged in trying to access profile is reditect to login
    '''
    url = reverse('profile')
    resp = client.get(url)

    assert resp.status_code == HTTPStatus.FOUND
    assert resp.url == f'{reverse("login")}?next={url}'


def test_login_page_redirect(client, django_user_model):
    '''
    After login the user is redirect for profile
    '''
    user_form_login = dict(username='test@email.com', password='1234')

    django_user_model.objects.create_user(email=user_form_login['username'],
                                          password=user_form_login['password'])

    resp = client.post(reverse('login'), data=user_form_login)

    assert resp.status_code == HTTPStatus.FOUND
    assert f'{resp.url}/' == f'{reverse("profile")}'


def test_profile_for_login(client, django_user_model):
    '''
    Profile page access for Logged user
    '''

    email, password = 'test@email.com', '1234'

    django_user_model.objects.create_user(email=email, password=password)

    client.login(email=email, password=password)

    response = client.get(reverse('profile'))

    assert response.status_code == HTTPStatus.OK
