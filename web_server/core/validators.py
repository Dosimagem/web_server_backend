import requests
from django.forms import ValidationError

# from django.utils.translation import gettext_lazy as _
from phonenumber_field.validators import validate_international_phonenumber
from validate_docbr import CNPJ, CPF


def validate_cpf(value):
    cpf = CPF()

    if not cpf.validate(value):
        # TODO: Translation:
        # raise ValidationError(_('CPF invalid.'), 'invalid.')
        raise ValidationError('CPF inválido.', 'invalid_cpf.')


def validate_cnpj(value):

    cnpj = CNPJ()

    if not cnpj.validate(value):
        # TODO: Translation:
        # raise ValidationError(_('CNPJ invalid.'), 'invalid.')
        raise ValidationError('CNPJ inválido.', 'invalid_cnpj.')

    URL_API = f'https://brasilapi.com.br/api/cnpj/v1/{value}'

    response = requests.get(URL_API)

    if response.status_code == 404:
        message = response.json()['message']
        raise ValidationError(message, 'invalid_by_api')


def validate_phone(value):
    validate_international_phonenumber(value)


def validate_name_is_alpha(value):
    if not value.replace(' ', '').replace('.', '').isalpha():
        raise ValidationError('O nome não pode ter números.', code='invalid_char')
