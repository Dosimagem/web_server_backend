from validate_docbr import CPF
from django.forms import ValidationError
from django.utils.translation import gettext_lazy as _


def validate_cpf(value):
    cpf = CPF()

    if not cpf.validate(value):
        raise ValidationError(_('CPF invalid'), 'cpf_invalid')
