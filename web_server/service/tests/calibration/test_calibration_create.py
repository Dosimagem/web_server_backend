from copy import deepcopy
from http import HTTPStatus

import pytest
from django.shortcuts import resolve_url

from web_server.service.models import FORMAT_DATE, Calibration

# /api/v1/users/<uuid>/calibrations/ - POST


def test_successful(client_api_auth, user, form_data, calibration_infos, calibration_file):

    assert not Calibration.objects.exists()

    url = resolve_url('service:calibration-list-create', user.uuid)

    form_data.update(calibration_file)

    response = client_api_auth.post(url, data=form_data, format='multipart')

    assert response.status_code == HTTPStatus.CREATED

    body = response.json()

    cali_db = Calibration.objects.first()

    expected = f'/api/v1/users/{ cali_db.user.uuid}/calibrations/{cali_db.uuid}/'

    assert expected == response.headers['Location']

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


def test_fail_negative_float_numbers(client_api_auth, user, form_data):

    url = resolve_url('service:calibration-list-create', user.uuid)

    form_data['syringeActivity'] = -form_data['syringeActivity']
    form_data['residualSyringeActivity'] = -form_data['residualSyringeActivity']
    form_data['phantomVolume'] = -form_data['phantomVolume']
    form_data['acquisitionTime'] = -form_data['acquisitionTime']

    response = client_api_auth.post(url, data=form_data, format='multipart')

    assert response.status_code == HTTPStatus.BAD_REQUEST

    body = response.json()

    assert not Calibration.objects.exists()

    expected = [
        'syringe_activity: Certifique-se que este valor seja maior ou igual a 0.0.',
        'residual_syringe_activity: Certifique-se que este valor seja maior ou igual a 0.0.',
        'phantom_volume: Certifique-se que este valor seja maior ou igual a 0.0.',
        'acquisition_time: Certifique-se que este valor seja maior ou igual a 0.0.',
    ]

    assert body['errors'] == expected


def test_fail_calibration_name_must_be_unique_per_user(client_api_auth, user, form_data):

    url = resolve_url('service:calibration-list-create', user.uuid)

    images = deepcopy(form_data['images'])

    response = client_api_auth.post(url, data=form_data, format='multipart')

    assert response.status_code == HTTPStatus.CREATED

    form_data['images'] = images

    response = client_api_auth.post(url, data=form_data, format='multipart')

    assert response.status_code == HTTPStatus.BAD_REQUEST

    body = response.json()

    expected = ['Calibração com este User e Calibration Name já existe.']

    assert body['errors'] == expected


def test_fail_datetime_invalid(client_api_auth, user, form_data):

    url = resolve_url('service:calibration-list-create', user.uuid)

    form_data['measurementDatetime'] = 'wrong'

    response = client_api_auth.post(url, data=form_data, format='multipart')

    assert response.status_code == HTTPStatus.BAD_REQUEST

    body = response.json()

    assert not Calibration.objects.exists()

    assert body['errors'] == ['measurement_datetime: Informe uma data/hora válida.']


def test_fail_isotope_invalid(client_api_auth, user, form_data):

    url = resolve_url('service:calibration-list-create', user.uuid)

    form_data['isotope'] = 'wrong'

    response = client_api_auth.post(url, data=form_data, format='multipart')

    assert response.status_code == HTTPStatus.BAD_REQUEST

    body = response.json()

    assert not Calibration.objects.exists()

    expected = ['isotope: Isótopo não registrado.']

    assert body['errors'] == expected


def test_fail_isotope_invalid_by_size(client_api_auth, user, form_data):

    url = resolve_url('service:calibration-list-create', user.uuid)

    form_data['isotope'] = 'more 6 char'

    response = client_api_auth.post(url, data=form_data, format='multipart')

    assert response.status_code == HTTPStatus.BAD_REQUEST

    body = response.json()

    assert not Calibration.objects.exists()

    expected = ['isotope: Certifique-se de que o valor tenha no máximo 6 caracteres (ele possui 11).']

    assert body['errors'] == expected


@pytest.mark.parametrize(
    'field, error',
    [
        ('isotope', ['isotope: Este campo é obrigatório.']),
        ('calibrationName', ['calibration_name: Este campo é obrigatório.']),
        ('syringeActivity', ['syringe_activity: Este campo é obrigatório.']),
        (
            'residualSyringeActivity',
            ['residual_syringe_activity: Este campo é obrigatório.'],
        ),
        ('measurementDatetime', ['measurement_datetime: Este campo é obrigatório.']),
        ('phantomVolume', ['phantom_volume: Este campo é obrigatório.']),
        # TODO: Verificar se vai realmente tirar esse campo ou não
        # ('acquisitionTime', ['acquisition_time: Este campo é obrigatório.']),
        ('images', ['images: Este campo é obrigatório.']),
    ],
)
def test_fail_missing_fields(client_api_auth, user, form_data, field, error):

    form_data.pop(field)

    url = resolve_url('service:calibration-list-create', user.uuid)

    response = client_api_auth.post(url, data=form_data, format='multipart')

    assert response.status_code == HTTPStatus.BAD_REQUEST

    body = response.json()

    assert not Calibration.objects.exists()

    assert body['errors'] == error


def test_fail_calibration_name_length_must_least_3(client_api_auth, user, form_data):

    url = resolve_url('service:calibration-list-create', user.uuid)

    form_data['calibrationName'] = 'mo'

    response = client_api_auth.post(url, data=form_data, format='multipart')

    assert response.status_code == HTTPStatus.BAD_REQUEST

    body = response.json()

    assert not Calibration.objects.exists()

    expected = ['calibration_name: Certifique-se de que o valor tenha no mínimo 3 caracteres (ele possui 2).']

    assert body['errors'] == expected
