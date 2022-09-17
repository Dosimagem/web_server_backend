
import requests
from validate_docbr import CPF, CNPJ
from django.forms import ValidationError
from django.utils.translation import gettext_lazy as _


def validate_cpf(value):
    cpf = CPF()

    if not cpf.validate(value):
        raise ValidationError(_('CPF invalid.'), 'invalid.')


def validate_cnpj(value):

    cnpj = CNPJ()

    if not cnpj.validate(value):
        raise ValidationError(_('CNPJ invalid.'), 'invalid.')

    URL_API = f'https://brasilapi.com.br/api/cnpj/v1/{value}'

    response = requests.get(URL_API)

    if response.status_code == 404:
        message = response.json()['message']
        raise ValidationError(message, 'invalid_by_api')
