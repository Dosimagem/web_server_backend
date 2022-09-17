from django.conf import settings


# TODO: Gambirras

LANG = settings.LANGUAGE_CODE
USE_I18N = settings.USE_I18N

if LANG == 'pt-br' and USE_I18N:
    MSG_ERROR_USER_ORDER = ['Este usuário não possui registro de pedido.']
    MSG_ERROR_USER_CALIBRATIONS = ['Este usuário não possui registro de calibrações.']
    MSG_ERROR_TOKEN_USER = ['O token e o ID do usuário não correspondem.']
    MSG_ERROR_RESOURCE = ['Este usuário não possui este recurso cadastrado.']
else:
    MSG_ERROR_USER_ORDER = ['This user has no order record.']
    MSG_ERROR_USER_CALIBRATIONS = ['This user has no calibrations record.']
    MSG_ERROR_TOKEN_USER = ['Token and User id do not match.']
    MSG_ERROR_RESOURCE = ['This user does not have this resource registered.']


ERRORS_MAP_EN = {
    'syringe_activity': 'syringe activity',
    'residual_syringe_activity': 'residual syringe activity',
    'measurement_datetime': 'measurement datetime',
    'phantom_volume': 'phantom volume',
    'acquisition_time': 'acquisition time',
    'confirmed_email': 'confirmed email',
    'role': 'role',
    'username': 'username',
    'password': 'password',
    'email': 'email',
    'phone': 'phone',
    'clinic': 'clinic',
    'name': 'name',
    'isotope': 'isotope',
    'calibration_name': 'calibration name',
    'images': 'images'
}

ERRORS_MAP_PT = {
    'syringe_activity': 'atividade da seringa',
    'residual_syringe_activity': 'atividade residual na seringa',
    'measurement_datetime': 'hora e data da medição',
    'phantom_volume': 'volume do fantoma',
    'acquisition_time': 'tempo de aquisição',
    'confirmed_email': 'email de confirmação',
    'role': 'cargo',
    'username': 'username',
    'password': 'senha',
    'email': 'email',
    'phone': 'telefone',
    'clinic': 'clínica',
    'name': 'nome',
    'cnpj': 'CNPJ',
    'cpf': 'CPF',
    'isotope': 'isotopo',
    'calibration_name': 'Nome da calibração',
    'images': 'images'
}


def list_errors(errors):

    list_ = []

    for field_name, field_errors in errors.items():
        for error in field_errors:
            if LANG == 'pt-br' and USE_I18N:
                if error == 'Este campo é obrigatório.':
                    name = ERRORS_MAP_PT[field_name]
                    msg = f'O campo {name} é obrigatório.'
                    list_.append(msg)
                elif error == 'Certifique-se que este valor seja maior ou igual a 0.0.':
                    name = ERRORS_MAP_PT[field_name]
                    msg = f'Certifique-se que {name} seja maior ou igual a 0.0.'
                    list_.append(msg)
                elif error == 'Calibration com este User e Calibration Name já existe.':
                    msg = 'Calibração com esse nome ja existe para este usuário.'
                    list_.append(msg)
                elif error == 'Isotope not registered.':
                    msg = 'Isotopo não registrado.'
                    list_.append(msg)
                elif error.startswith('Certifique-se de que o valor tenha no máximo') and field_name == 'isotope':
                    msg = 'Isotopo inválido.'
                    list_.append(msg)
                elif error.startswith('Certifique-se de que o valor tenha no máximo') and field_name == 'cnpj':
                    msg = 'CNPJ inválido.'
                    list_.append(msg)
                elif error.endswith('already exists'):
                    name = ERRORS_MAP_PT[field_name].capitalize()
                    name = 'CPF' if name == 'Cpf' else name
                    name = 'CNPJ' if name == 'Cnpj' else name
                    msg = f'{name} já existe.'
                    list_.append(msg)
                elif error == 'The two email fields didn’t match.':
                    msg = 'Os campos emails não correspondem.'
                    list_.append(msg)
                else:
                    list_.append(error)
            else:
                if error == 'This field is required.':
                    name = ERRORS_MAP_EN[field_name].capitalize()
                    msg = error.replace('This', name)
                    list_.append(msg)
                elif error == 'Ensure this value is greater than or equal to 0.0.':
                    name = ERRORS_MAP_EN[field_name]
                    msg = error.replace('this', name)
                    list_.append(msg)
                elif error.startswith('Ensure this value has at most') and field_name == 'isotope':
                    msg = 'Invalid isotope.'
                    list_.append(msg)
                else:
                    list_.append(error)

    return list_
