from http import HTTPStatus
from uuid import uuid4

from django.shortcuts import resolve_url

from web_server.core.errors_msg import MSG_ERROR_TOKEN_USER

# /api/v1/users/<uuid>/budget - POST

END_POINT = 'budget:general-budget'


def test_wrong_service_name(client_api_auth, user):

    url = resolve_url(END_POINT, user.uuid)

    resp = client_api_auth.post(url, data={'service': 'Service wrong'})

    assert HTTPStatus.BAD_REQUEST == resp.status_code

    body = resp.json()
    assert ['service: "Service wrong" não é um escolha válido.'] == body['errors']


def test_not_allowed_method(client_api_auth):

    url = resolve_url(END_POINT, uuid4())

    resp = client_api_auth.put(url)
    assert HTTPStatus.METHOD_NOT_ALLOWED == resp.status_code

    resp = client_api_auth.patch(url)
    assert HTTPStatus.METHOD_NOT_ALLOWED == resp.status_code

    resp = client_api_auth.delete(url)
    assert HTTPStatus.METHOD_NOT_ALLOWED == resp.status_code

    resp = client_api_auth.get(url)
    assert HTTPStatus.METHOD_NOT_ALLOWED == resp.status_code


def test_auth(client_api):

    url = resolve_url(END_POINT, uuid4())

    resp = client_api.post(url)
    body = resp.json()

    assert HTTPStatus.UNAUTHORIZED == resp.status_code

    assert 'As credenciais de autenticação não foram fornecidas.' == body['detail']


def test_user_not_have_email_verified(client_api_auth, user):

    url = resolve_url(END_POINT, user.uuid)

    user.email_verified = False
    user.save()

    resp = client_api_auth.post(url)
    body = resp.json()

    assert HTTPStatus.CONFLICT == resp.status_code

    assert ['O usuário ainda não possui um e-mail verificado.'] == body['errors']


def test_token_id_and_user_id_dont_match(client_api_auth, user):

    url = resolve_url(END_POINT, uuid4())
    response = client_api_auth.post(url)

    assert HTTPStatus.UNAUTHORIZED == response.status_code

    body = response.json()

    assert MSG_ERROR_TOKEN_USER == body['errors']
