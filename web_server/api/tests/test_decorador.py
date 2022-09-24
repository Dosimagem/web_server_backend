from uuid import uuid4
from http import HTTPStatus
from unittest.mock import MagicMock

from rest_framework.response import Response

from web_server.api.decorators import user_from_token_and_user_from_url


@user_from_token_and_user_from_url
def mock_view(request, user_id):
    return Response({'data': 'success'})


def test_decorador_user_and_user_token_dont_match(mocker):

    request = MagicMock()
    user = {}

    request.user.uuid = uuid4()
    user = uuid4()

    resp = mock_view(request, user_id=user)

    assert resp.status_code == HTTPStatus.UNAUTHORIZED

    assert resp.data == {'errors': ['O token e o ID do usuário não correspondem.']}


def test_decorador_user_and_user_token_match(mocker):

    request = MagicMock()
    user = {}

    uuid = uuid4()

    request.user.uuid = uuid
    user = uuid

    resp = mock_view(request, user_id=user)

    assert resp.status_code == HTTPStatus.OK

    assert resp.data == {'data': 'success'}
