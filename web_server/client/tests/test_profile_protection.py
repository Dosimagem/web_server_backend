from http import HTTPStatus

from django.urls import reverse


def test_profile_redirect_for_login_page_user_not_login(client):
    '''
    User not logged in trying to access the profile must be redirected to login
    '''
    url = reverse('profile')
    resp = client.get(url)

    assert resp.status_code == HTTPStatus.FOUND
    assert resp.url == f'{reverse("login")}?next={url}'


def test_profile_for_login(client, django_user_model):
    '''
    Profile page must be accessible to logged in users
    '''

    email, password = 'test@email.com', '1234'

    django_user_model.objects.create_user(email=email, password=password)

    client.login(email=email, password=password)

    response = client.get(reverse('profile'))

    assert response.status_code == HTTPStatus.OK
