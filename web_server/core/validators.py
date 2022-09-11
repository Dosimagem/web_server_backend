from validate_docbr import CPF, CNPJ
from django.forms import ValidationError
from django.utils.translation import gettext_lazy as _


def validate_cpf(value):
    cpf = CPF()

    if not cpf.validate(value):
        raise ValidationError(_('CPF invalid.'), 'invalid.')


def validate_cnpf(value):
    cnpj = CNPJ()

    if not cnpj.validate(value):
        raise ValidationError(_('CNPJ invalid.'), 'invalid.')
