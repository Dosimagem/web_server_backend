def list_errors(errors):

    list_ = []

    for field_name, field_errors in errors.items():
        for error in field_errors:
            msg = error

            if 'Faça uma escolha válida' in error:
                if field_name == 'radionuclide':
                    msg = 'Radionicleotideo inválido.'
                elif field_name == 'thickness':
                    msg = 'Espessura sinovial inválida.'

            elif 'Certifique-se que este valor seja maior ou igual a 0.0.' in error:
                msg = 'Certifique-se que o valor da superfície seja maior ou igual a 0.0.'

            elif 'Informe um número.' in error:
                msg = 'Superficie precisa ser um número.'

            elif 'Este campo é obrigatório.' in error:
                if field_name == 'radionuclide':
                    msg = 'Radionicleotideo é obrigatório.'
                elif field_name == 'thickness':
                    msg = 'Espessura é obrigatório.'
                elif field_name == 'surface':
                    msg = 'Superfície é obrigatório.'

            list_.append(msg)

    return list_
