MSG_ERROR_TOKEN_USER = ['O token e o ID do usuário não correspondem.']
MSG_ERROR_RESOURCE = ['Este usuário não possui este recurso cadastrado.']
ERROR_CALIBRATION_ID = ['Calibração com esse id não existe para esse usuário.']

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
    'administration_datetime': 'hora e data de adminstração',
    'surface': 'superfície',
    'thickness': 'espessura',
    'radionuclide': 'radionicleotideo',
}


def list_errors(errors):

    list_ = []

    for field_name, field_errors in errors.items():
        for error in field_errors:

            if field_name == '__all__' or field_name == 'non_field_errors':
                msg = error
            else:
                msg = f'{field_name}: {error}'
            list_.append(msg)

    return list_



# def list_errors(errors):

#     list_ = []

#     for field_name, field_errors in errors.items():
#         for error in field_errors:

#             msg = f'{field_name}: {error}'

#             # if error == 'Este campo é obrigatório.':
#             #     name = ERRORS_MAP_PT.get(field_name, field_name)
#             #     msg = f'O campo {name} é obrigatório.'

#             # elif error == 'Certifique-se que este valor seja maior ou igual a 0.0.':
#             #     name = ERRORS_MAP_PT.get(field_name, field_name)
#             #     msg = f'Certifique-se que {name} seja maior ou igual a 0.0.'

#             # elif error == 'Calibration com este User e Calibration Name já existe.':
#             #     msg = 'Calibração com esse nome ja existe para este usuário.'

#             # elif (
#             #     error == 'Preclinic Dosimetry com este Order e Analysis Name já existe.'
#             #     or error == 'Clinic Dosimetry com este Order e Analysis Name já existe.'
#             #     or error == 'Segmentation Analysis com este Order e Analysis Name já existe.'
#             #     or error == 'Radiosynoviorthesis Analysis com este Order e Analysis Name já existe.'
#             # ):
#             #     msg = 'Análises com esse nome já existe para esse pedido.'

#             # elif error == 'Isotope not registered.':
#             #     msg = 'Isotopo não registrado.'

#             # elif error.startswith('Certifique-se de que o valor tenha no máximo') and field_name == 'isotope':
#             #     msg = 'Isotopo inválido.'

#             # elif error.startswith('Certifique-se de que o valor tenha no máximo') and field_name == 'cnpj':
#             #     msg = 'CNPJ inválido.'

#             # elif error.endswith('already exists'):
#             #     name = ERRORS_MAP_PT.get(field_name, field_name).capitalize()
#             #     name = 'CPF' if name == 'Cpf' else name
#             #     name = 'CNPJ' if name == 'Cnpj' else name
#             #     msg = f'{name} já existe.'

#             # elif error == 'The two email fields didn’t match.':
#             #     msg = 'Os campos emails não correspondem.'

#             # elif error == 'CNPJ invalid.':
#             #     msg = 'CNPJ inválido.'

#             # elif error == 'CPF invalid.':
#             #     msg = 'CPF inválido.'

#             # elif error.startswith('Certifique-se de que o valor tenha no mínimo 3 caracteres'):
#             #     if field_name == 'calibration_name':
#             #         msg = 'Certifique-se de que o nome da calibração tenha no mínimo 3 caracteres.'
#             #     elif field_name == 'analysis_name':
#             #         msg = 'Certifique-se de que o nome da análise tenha no mínimo 3 caracteres.'
#             #     elif field_name == 'name':
#             #         msg = 'Certifique-se de que o nome tenha no mínimo 3 caracteres.'

#             # elif 'Faça uma escolha válida' in error:
#             #     if field_name == 'radionuclide':
#             #         msg = 'Radionicleotideo inválido.'
#             #     elif field_name == 'thickness':
#             #         msg = 'Espessura sinovial inválida.'

#             # # elif 'Certifique-se que este valor seja maior ou igual a 0.0.' in error:
#             # #     msg = 'Certifique-se que o valor da superfície seja maior ou igual a 0.0.'

#             # elif 'Informe um número.' in error and field_name == 'surface':
#             #     msg = 'Superficie precisa ser um número.'

#             list_.append(msg)

#     return list_
