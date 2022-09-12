from rest_framework.authentication import TokenAuthentication
from django.utils.translation import get_language
from django.conf import settings

class MyTokenAuthentication(TokenAuthentication):
    keyword = 'Bearer'


def list_errors(errors):

    lang = get_language()

    list_ = []

    for field_name, field_errors in errors.items():
        for error in field_errors:
            if lang == 'pt-br' and settings.USE_I18N :
                if error == 'Este campo é obrigatório.':
                    name = field_name
                    msg = f'Campo {name} é obrigatório.'
                    list_.append(msg)
                elif error == 'Certifique-se que este valor seja maior ou igual a 0.0.':
                    name = field_name
                    msg = f'Certifique-se que {name} valor seja maior ou igual a 0.0.'
                    list_.append(msg)
                else:
                    list_.append(error)
            else:
                if error == 'This field is required.':
                    name = field_name.capitalize()
                    msg = error.replace('This', name)
                    list_.append(msg)
                elif error == 'Ensure this value is greater than or equal to 0.0.':
                    name = field_name.capitalize()
                    msg = error.replace('this', name)
                    list_.append(msg)
                else:
                    list_.append(error)

    return list_
