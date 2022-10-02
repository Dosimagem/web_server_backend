import pytest


from django.forms import ValidationError


from web_server.core.validators import validate_phone


def test_mobile():
    phone = '55(21)98888-8888'

    validate_phone(phone)


def test_landline():
    phone = '55(21)8888-8888'
    validate_phone(phone)


def test_less_digits():
    phone = '2222222'

    with pytest.raises(ValidationError):
        validate_phone(phone)


def test_need_mask():
    phone = '552188888888'

    with pytest.raises(ValidationError):
        validate_phone(phone)


def test_with_country_code():
    phone = '(21)88888888'

    with pytest.raises(ValidationError):
        validate_phone(phone)
