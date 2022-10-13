import re

import requests
from django.forms import ValidationError
from django.utils.translation import gettext_lazy as _
from validate_docbr import CNPJ, CPF


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


def validate_phone(value):

    pattern = r'(\d{2})\(\d{2}\)(\d{4,5})(-)(\d{4})'

    match = re.search(pattern, value)

    if not match:
        raise ValidationError(
            'Número de telefone inválido. O formato deve ser xx(xx)xxxx-xxxx ou xx(xx)xxxxx-xxxx.',
            'phone_invalid',
        )
