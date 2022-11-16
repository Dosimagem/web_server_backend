from http import HTTPStatus
from uuid import uuid4

from django.shortcuts import resolve_url

from web_server.core.errors_msg import MSG_ERROR_TOKEN_USER
from web_server.notification.models import Notification

# /api/v1/users/<uuid>/notifications/<uuid>/toogle_cheked/ - POST

END_POINT = 'notification:toogle-check'


def test_cheked_flase2true(client_api_auth, user, notification):

    url = resolve_url(END_POINT, user.uuid, notification.uuid)

    resp = client_api_auth.post(url)

    assert not notification.checked

    assert HTTPStatus.NO_CONTENT == resp.status_code

    notification.refresh_from_db()

    assert notification.checked


def test_cheked_true2false(client_api_auth, user, faker):

    notification = Notification.objects.create(
        user=user, checked=True, message=faker.sentence(nb_words=10), kind=Notification.Kind.SUCCESS
    )

    url = resolve_url(END_POINT, user.uuid, notification.uuid)

    resp = client_api_auth.post(url)

    assert notification.checked

    assert HTTPStatus.NO_CONTENT == resp.status_code

    notification.refresh_from_db()

    assert not notification.checked


def test_list_not_allowed_method(client_api_auth, user):

    url = resolve_url(END_POINT, user.uuid, uuid4())

    resp = client_api_auth.get(url)
    assert resp.status_code == HTTPStatus.METHOD_NOT_ALLOWED

    resp = client_api_auth.put(url)
    assert resp.status_code == HTTPStatus.METHOD_NOT_ALLOWED

    resp = client_api_auth.patch(url)
    assert resp.status_code == HTTPStatus.METHOD_NOT_ALLOWED

    resp = client_api_auth.delete(url)
    assert resp.status_code == HTTPStatus.METHOD_NOT_ALLOWED


def test_allowed_method(client_api_auth, user):

    url = resolve_url(END_POINT, user.uuid, uuid4())

    resp = client_api_auth.options(url)

    assert resp.status_code == HTTPStatus.OK

    options = resp.headers['Allow'].split(',')

    for o in options:
        assert o.strip() in ['OPTIONS', 'POST']


def test_token_id_and_user_id_dont_match(client_api_auth, user):

    url = resolve_url(END_POINT, uuid4(), uuid4())
    response = client_api_auth.post(url)

    assert response.status_code == HTTPStatus.UNAUTHORIZED

    body = response.json()

    assert body['errors'] == MSG_ERROR_TOKEN_USER


def test_fail_must_be_auth(client_api, user):

    url = resolve_url(END_POINT, user.uuid, uuid4())

    resp = client_api.get(url)
    body = resp.json()

    assert resp.status_code == HTTPStatus.UNAUTHORIZED
    assert body['detail'] == 'As credenciais de autenticação não foram fornecidas.'


def test_wrong_notification_id(client_api_auth, user):

    url = resolve_url(END_POINT, user.uuid, uuid4())

    resp = client_api_auth.post(url)

    assert HTTPStatus.NOT_FOUND == resp.status_code
