MSG_ERROR_TOKEN_USER = ['O token e o ID do usuário não correspondem.']
MSG_ERROR_RESOURCE = ['Este usuário não possui este recurso cadastrado.']


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
    'images': 'imagens',
    'calibration_id': 'id de calibração',
    'analysis_name': 'nome da análise',
    'injected_activity': 'atividade injetada',
    'administration_datetime': 'hora e data de adminstração'
}


def list_errors(errors):

    list_ = []

    for field_name, field_errors in errors.items():
        for error in field_errors:
            if error == 'Este campo é obrigatório.':
                name = ERRORS_MAP_PT.get(field_name, field_name)
                msg = f'O campo {name} é obrigatório.'
                list_.append(msg)
            elif error == 'Certifique-se que este valor seja maior ou igual a 0.0.':
                name = ERRORS_MAP_PT.get(field_name, field_name)
                msg = f'Certifique-se que {name} seja maior ou igual a 0.0.'
                list_.append(msg)
            elif error == 'Calibration com este User e Calibration Name já existe.':
                msg = 'Calibração com esse nome ja existe para este usuário.'
                list_.append(msg)
            elif (error == 'Preclinic Dosimetry com este Order e Analysis Name já existe.'
                    or
                  error == 'Clinic Dosimetry com este Order e Analysis Name já existe.'
                  ):
                msg = 'Análises com esse nome já existe para esse pedido.'
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
                name = ERRORS_MAP_PT.get(field_name, field_name).capitalize()
                name = 'CPF' if name == 'Cpf' else name
                name = 'CNPJ' if name == 'Cnpj' else name
                msg = f'{name} já existe.'
                list_.append(msg)
            elif error == 'The two email fields didn’t match.':
                msg = 'Os campos emails não correspondem.'
                list_.append(msg)
            elif error == 'CNPJ invalid.':
                msg = 'CNPJ inválido.'
                list_.append(msg)
            elif error == 'CPF invalid.':
                msg = 'CPF inválido.'
                list_.append(msg)
            else:
                list_.append(error)

    return list_
