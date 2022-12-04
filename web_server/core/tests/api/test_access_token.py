from http import HTTPStatus

from dj_rest_auth.utils import jwt_encode
from django.shortcuts import resolve_url
from freezegun import freeze_time


def test_access_token(client_api_auth, user):

    url = resolve_url('core:am-i-auth')

    response = client_api_auth.get(url)

    assert response.status_code == HTTPStatus.OK

    body = response.json()

    expected = {'message': f'{user.profile.name} is authenticated.'}

    assert expected == body


@freeze_time('2022-01-01', auto_tick_seconds=15 * 60)
def test_expire_access_token(client_api, user):

    url = resolve_url('core:am-i-auth')

    access_token, _ = jwt_encode(user)
    client_api.cookies.load({'jwt-access-token': access_token})
    response = client_api.get(url)

    assert response.status_code == HTTPStatus.UNAUTHORIZED

    body = response.json()

    expected = {
        'code': 'token_not_valid',
        'detail': 'Given token not valid for any token type',
        'messages': [{'message': 'Token is invalid or expired', 'tokenClass': 'AccessToken', 'tokenType': 'access'}],
    }

    assert expected == body
