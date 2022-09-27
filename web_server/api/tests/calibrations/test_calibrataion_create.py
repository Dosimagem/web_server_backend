from copy import deepcopy
from http import HTTPStatus

import pytest
from django.shortcuts import resolve_url

from web_server.service.models import Calibration, FORMAT_DATE


def test_create_successful(client_api_auth, user, form_data, calibration_infos, calibration_file):
    '''
    /api/v1/users/<uuid>/calibrations/ - POST
    '''

    assert not Calibration.objects.exists()

    url = resolve_url('api:calibration-list-create', user.uuid)

    form_data.update(calibration_file)

    response = client_api_auth.post(url, data=form_data, format='multipart')

    assert response.status_code == HTTPStatus.CREATED

    body = response.json()

    cali_db = Calibration.objects.first()

    assert Calibration.objects.exists()

    assert body['id'] == str(cali_db.uuid)
    assert body['userId'] == str(calibration_infos['user'].uuid)
    assert body['isotope'] == calibration_infos['isotope'].name
    assert body['calibrationName'] == calibration_infos['calibration_name']
    assert body['syringeActivity'] == calibration_infos['syringe_activity']
    assert body['residualSyringeActivity'] == calibration_infos['residual_syringe_activity']
    assert body['measurementDatetime'] == calibration_infos['measurement_datetime'].strftime(FORMAT_DATE)
    assert body['phantomVolume'] == calibration_infos['phantom_volume']
    assert body['acquisitionTime'] == calibration_infos['acquisition_time']
    # TODO: Pensar um forma melhor
    assert body['imagesUrl'].startswith(f'http://testserver/media/{cali_db.user.id}/calibration')


def test_fail_create_negative_float_numbers(client_api_auth, user, form_data):
    '''
    /api/v1/users/<uuid>/calibrations/ - POST
    '''

    url = resolve_url('api:calibration-list-create', user.uuid)

    form_data['syringeActivity'] = -form_data['syringeActivity']
    form_data['residualSyringeActivity'] = -form_data['residualSyringeActivity']
    form_data['phantomVolume'] = -form_data['phantomVolume']
    form_data['acquisitionTime'] = -form_data['acquisitionTime']

    response = client_api_auth.post(url, data=form_data, format='multipart')

    assert response.status_code == HTTPStatus.BAD_REQUEST

    body = response.json()

    assert not Calibration.objects.exists()

    expected = [
        'Certifique-se que atividade da seringa seja maior ou igual a 0.0.',
        'Certifique-se que atividade residual na seringa seja maior ou igual a 0.0.',
        'Certifique-se que volume do fantoma seja maior ou igual a 0.0.',
        'Certifique-se que tempo de aquisição seja maior ou igual a 0.0.',
    ]

    assert body['errors'] == expected


def test_fail_create_calibration_name_must_be_unique_per_user(client_api_auth, user, form_data):
    '''
    /api/v1/users/<uuid>/calibrations/ - POST
    '''

    url = resolve_url('api:calibration-list-create', user.uuid)

    images = deepcopy(form_data['images'])

    response = client_api_auth.post(url, data=form_data, format='multipart')

    assert response.status_code == HTTPStatus.CREATED

    form_data['images'] = images

    response = client_api_auth.post(url, data=form_data, format='multipart')

    assert response.status_code == HTTPStatus.BAD_REQUEST

    body = response.json()

    expected = ['Calibração com esse nome ja existe para este usuário.']

    assert body['errors'] == expected


def test_fail_create_datetime_invalid(client_api_auth, user, form_data):
    '''
    /api/v1/users/<uuid>/calibrations/ - POST
    '''

    url = resolve_url('api:calibration-list-create', user.uuid)

    form_data['measurementDatetime'] = 'wrong'

    response = client_api_auth.post(url, data=form_data, format='multipart')

    assert response.status_code == HTTPStatus.BAD_REQUEST

    body = response.json()

    assert not Calibration.objects.exists()

    assert body['errors'] == ['Informe uma data/hora válida.']


def test_fail_create_isotope_invalid(client_api_auth, user, form_data):
    '''
    /api/v1/users/<uuid>/calibrations/ - POST
    '''

    url = resolve_url('api:calibration-list-create', user.uuid)

    form_data['isotope'] = 'wrong'

    response = client_api_auth.post(url, data=form_data, format='multipart')

    assert response.status_code == HTTPStatus.BAD_REQUEST

    body = response.json()

    assert not Calibration.objects.exists()

    expected = ['Isotopo não registrado.']

    assert body['errors'] == expected


def test_fail_create_isotope_invalid_by_size(client_api_auth, user, form_data):
    '''
    /api/v1/users/<uuid>/calibrations/ - POST
    '''

    url = resolve_url('api:calibration-list-create', user.uuid)

    form_data['isotope'] = 'more 6 char'

    response = client_api_auth.post(url, data=form_data, format='multipart')

    assert response.status_code == HTTPStatus.BAD_REQUEST

    body = response.json()

    assert not Calibration.objects.exists()

    expected = ['Isotopo inválido.']

    assert body['errors'] == expected


@pytest.mark.parametrize('field, error', [
    ('isotope', ['O campo isotopo é obrigatório.']),
    ('calibrationName', ['O campo Nome da calibração é obrigatório.']),
    ('syringeActivity', ['O campo atividade da seringa é obrigatório.']),
    ('residualSyringeActivity', ['O campo atividade residual na seringa é obrigatório.']),
    ('measurementDatetime', ['O campo hora e data da medição é obrigatório.']),
    ('phantomVolume', ['O campo volume do fantoma é obrigatório.']),
    ('acquisitionTime', ['O campo tempo de aquisição é obrigatório.']),
    ('images', ['O campo imagens é obrigatório.']),
    ])
def test_fail_create_missing_fields(client_api_auth, user, form_data, field, error):
    '''
    /api/v1/users/<uuid>/calibrations/ - POST
    '''

    form_data.pop(field)

    url = resolve_url('api:calibration-list-create', user.uuid)

    response = client_api_auth.post(url, data=form_data, format='multipart')

    assert response.status_code == HTTPStatus.BAD_REQUEST

    body = response.json()

    assert not Calibration.objects.exists()

    assert body['errors'] == error
