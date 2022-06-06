from http import HTTPStatus

from django.urls import reverse


def test_redirect_for_login_page_user_not_login(client):
    '''
    User not logged in go to login
    '''
    url = reverse('profile')
    resp = client.get(url)

    assert resp.status_code == HTTPStatus.FOUND
    assert resp.url == f'{reverse("login")}?next={url}'


def test_login_page_redirect(client, django_user_model):
    '''
    After login redirect for user profile
    '''
    user_form_login = dict(username='test@email.com', password='1234')

    django_user_model.objects.create_user(email=user_form_login['username'],
                                          password=user_form_login['password'])

    resp = client.post(reverse('login'), data=user_form_login)

    assert resp.status_code == HTTPStatus.FOUND
    assert f'{resp.url}/' == f'{reverse("profile")}'
