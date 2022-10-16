import pytest
from django.forms import ValidationError

from web_server.core.validators import validate_name_is_alpha


def test_name():
    phone = 'User'

    validate_name_is_alpha(phone)


def test_is_alpha():
    phone = 'User 1'

    with pytest.raises(ValidationError):
        validate_name_is_alpha(phone)
