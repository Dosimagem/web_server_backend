from datetime import datetime

import pytest
from django.conf import settings
from freezegun import freeze_time
from jwt import decode
from jwt.exceptions import ExpiredSignatureError

from web_server.core.views.register import _jwt_verification_email_secret


def test_token_verify_email_expiration_time(user):

    initial_datetime = datetime(year=2000, month=1, day=1)

    with freeze_time(initial_datetime) as frozen_datetime:

        token = _jwt_verification_email_secret(user)

        payload = decode(token, settings.SECRET_KEY, algorithms=['HS256'])

        assert str(user.uuid) == payload['id']

        frozen_datetime.move_to('2000-1-2')

        with pytest.raises(ExpiredSignatureError):
            decode(token, settings.SECRET_KEY, algorithms=['HS256'])
