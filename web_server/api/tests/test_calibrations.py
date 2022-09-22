from copy import deepcopy
from http import HTTPStatus
from uuid import uuid4

import pytest
from django.shortcuts import resolve_url
from django.utils.translation import gettext as _

from web_server.service.models import Calibration, FORMAT_DATE
from web_server.api.views.errors_msg import (
    LANG,
    USE_I18N,
    MSG_ERROR_TOKEN_USER,
    MSG_ERROR_RESOURCE,
)


def test_list_create_not_allowed_method(client_api_auth, calibration):
    '''
    /api/v1/users/<uuid>/calibrations/ - GET, POST
    '''

    url = resolve_url('api:calibration-list-create', calibration.user.uuid)

    resp = client_api_auth.put(url, format='json')
    assert resp.status_code == HTTPStatus.METHOD_NOT_ALLOWED

    resp = client_api_auth.patch(url, format='json')
    assert resp.status_code == HTTPStatus.METHOD_NOT_ALLOWED

    resp = client_api_auth.delete(url, format='json')
    assert resp.status_code == HTTPStatus.METHOD_NOT_ALLOWED


def test_list_create_token_view_and_user_id_dont_match(client_api_auth, calibration):
    '''
    /api/v1/users/<uuid>/calibrations/ - GET, POST
    The token does not belong to the user
    '''

    url = resolve_url('api:calibration-list-create', uuid4())
    response = client_api_auth.get(url)

    assert response.status_code == HTTPStatus.UNAUTHORIZED

    body = response.json()

    assert body['errors'] == MSG_ERROR_TOKEN_USER


def test_list_successful(client_api_auth, calibration):
    '''
    /api/v1/users/<uuid>/calibrations/ - GET
    '''

    url = resolve_url('api:calibration-list-create', calibration.user.uuid)

    response = client_api_auth.get(url)

    body = response.json()

    assert response.status_code == HTTPStatus.OK

    calibration_db = list(Calibration.objects.filter(user=calibration.user))

    calibration_response_list = body['row']

    assert body['count'] == 1

    for cali_response, cali_db in zip(calibration_response_list, calibration_db):
        assert cali_response['id'] == str(cali_db.uuid)
        assert cali_response['userId'] == str(cali_db.user.uuid)
        assert cali_response['isotope'] == cali_db.isotope.name
        assert cali_response['calibrationName'] == cali_db.calibration_name
        assert cali_response['syringeActivity'] == cali_db.syringe_activity
        assert cali_response['residualSyringeActivity'] == cali_db.residual_syringe_activity
        assert cali_response['measurementDatetime'] == cali_db.measurement_datetime.strftime(FORMAT_DATE)
        assert cali_response['phantomVolume'] == cali_db.phantom_volume
        assert cali_response['acquisitionTime'] == cali_db.acquisition_time


def test_try_list_for_user_without_calibrations(client_api_auth, user):
    '''
    /api/v1/users/<uuid>/calibrations/ - GET
    '''

    url = resolve_url('api:calibration-list-create', user.uuid)

    response = client_api_auth.get(url)

    assert response.status_code == HTTPStatus.OK

    body = response.json()

    assert body == {'count': 0, 'row': []}


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

    if LANG == 'pt-br' and USE_I18N:
        expected = [
            'Certifique-se que atividade da seringa seja maior ou igual a 0.0.',
            'Certifique-se que atividade residual na seringa seja maior ou igual a 0.0.',
            'Certifique-se que volume do fantoma seja maior ou igual a 0.0.',
            'Certifique-se que tempo de aquisição seja maior ou igual a 0.0.',
            ]
    else:
        expected = [
            'Ensure syringe activity value is greater than or equal to 0.0.',
            'Ensure residual syringe activity value is greater than or equal to 0.0.',
            'Ensure phantom volume value is greater than or equal to 0.0.',
            'Ensure acquisition time value is greater than or equal to 0.0.'
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

    if LANG == 'pt-br' and USE_I18N:
        expected = ['Calibração com esse nome ja existe para este usuário.']
    else:
        expected = ['Calibration with this User and Calibration Name already exists.']

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

    assert body['errors'] == [_('Enter a valid date/time.')]


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

    if LANG == 'pt-br' and USE_I18N:
        expected = ['Isotopo não registrado.']
    else:
        expected = ['Isotope not registered.']

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

    if LANG == 'pt-br' and USE_I18N:
        expected = ['Isotopo inválido.']
    else:
        expected = ['Invalid isotope.']

    assert body['errors'] == expected


@pytest.mark.parametrize('field, error', [
    ('isotope', [
        'O campo isotopo é obrigatório.' if LANG and USE_I18N else 'Isotope field is required.'
        ]),
    ('calibrationName', [
        'O campo Nome da calibração é obrigatório.' if LANG and USE_I18N else 'Calibration name field is required.'
        ]),
    ('syringeActivity', [
        'O campo atividade da seringa é obrigatório.'
        if LANG and USE_I18N else 'Syringe activity field is required.'
        ]),
    ('residualSyringeActivity', [
        'O campo atividade residual na seringa é obrigatório.'
        if LANG and USE_I18N else 'Residual syringe activity field is required.'
        ]),
    ('measurementDatetime', [
        'O campo hora e data da medição é obrigatório.'
        if LANG and USE_I18N else 'Measurement datetime field is required.'
        ]),
    ('phantomVolume', [
        'O campo volume do fantoma é obrigatório.' if LANG and USE_I18N else 'Phantom volume field is required.'
        ]),
    ('acquisitionTime', [
        'O campo tempo de aquisição é obrigatório.' if LANG and USE_I18N else 'Acquisition time field is required.'
        ]),
    ('images', [
        'O campo imagens é obrigatório.' if LANG and USE_I18N else 'Images field is required.'
        ]),
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


def test_read_update_delete_not_allowed_method(client_api_auth, calibration):
    '''
    /api/v1/users/<uuid>/calibrations/<uuid> - GET, PUT, DELETE
    '''

    url = resolve_url('api:calibration-read-update-delete', calibration.user.uuid, calibration.uuid)

    resp = client_api_auth.patch(url, format='json')
    assert resp.status_code == HTTPStatus.METHOD_NOT_ALLOWED

    resp = client_api_auth.post(url, format='json')
    assert resp.status_code == HTTPStatus.METHOD_NOT_ALLOWED


def test_read_update_delete_view_and_user_id_dont_match(client_api_auth, calibration):
    '''
    /api/v1/users/<uuid>/calibrations/<uuid> - GET, PUT, DELETE
    The token does not belong to the user
    '''

    url = resolve_url('api:calibration-read-update-delete', uuid4(), calibration.uuid)
    response = client_api_auth.get(url)

    assert response.status_code == HTTPStatus.UNAUTHORIZED

    body = response.json()

    assert body['errors'] == MSG_ERROR_TOKEN_USER


def test_read_calibration_successful(client_api_auth, calibration_with_images):
    '''
    /api/v1/users/<uuid>/calibrations/<uuid> - GET
    '''

    url = resolve_url('api:calibration-read-update-delete',
                      calibration_with_images.user.uuid,
                      calibration_with_images.uuid)

    response = client_api_auth.get(url)

    assert response.status_code == HTTPStatus.OK

    body = response.json()

    cali = calibration_with_images

    assert body['id'] == str(cali.uuid)
    assert body['userId'] == str(cali.user.uuid)
    assert body['isotope'] == cali.isotope.name
    assert body['calibrationName'] == cali.calibration_name
    assert body['syringeActivity'] == cali.syringe_activity
    assert body['residualSyringeActivity'] == cali.residual_syringe_activity
    assert body['measurementDatetime'] == cali.measurement_datetime.strftime(FORMAT_DATE)
    assert body['phantomVolume'] == cali.phantom_volume
    assert body['acquisitionTime'] == cali.acquisition_time
    assert body['imagesUrl'].startswith(f'http://testserver/media/{cali.user.id}/calibration')


def test_fail_read_wrong_calibration_id(client_api_auth, calibration):
    '''
    /api/v1/users/<uuid>/calibrations/<uuid> - GET
    '''

    url = resolve_url('api:calibration-read-update-delete', calibration.user.uuid, uuid4())

    response = client_api_auth.get(url)

    assert response.status_code == HTTPStatus.NOT_FOUND

    body = response.json()

    assert body['errors'] == MSG_ERROR_RESOURCE


def test_fail_read_calibration_the_another_user(client_api_auth, calibration, second_user_calibrations):
    '''
    /api/v1/users/<uuid>/calibrations/<uuid> - GET
    '''

    second_user_calibration_uuid = second_user_calibrations[0].uuid

    url = resolve_url('api:calibration-read-update-delete', calibration.user.uuid, second_user_calibration_uuid)
    response = client_api_auth.get(url)

    assert response.status_code == HTTPStatus.NOT_FOUND

    body = response.json()

    assert body['errors'] == MSG_ERROR_RESOURCE


def test_delete_successful(client_api_auth, calibration):
    '''
    /api/v1/users/<uuid>/calibrations/<uuid> - DELETE
    '''

    url = resolve_url('api:calibration-read-update-delete', calibration.user.uuid, calibration.uuid)

    response = client_api_auth.delete(url)

    assert response.status_code == HTTPStatus.OK

    assert not Calibration.objects.exists()

    body = response.json()

    assert body['message'] == 'Calibração deletada com sucesso!'


def test_fail_delete_wrong_calibration_id(client_api_auth, calibration):
    '''
    /api/v1/users/<uuid>/calibrations/<uuid> - DELETE
    '''

    url = resolve_url('api:calibration-read-update-delete', calibration.user.uuid, uuid4())
    response = client_api_auth.delete(url)

    assert response.status_code == HTTPStatus.NOT_FOUND

    body = response.json()

    assert body['errors'] == MSG_ERROR_RESOURCE

    assert Calibration.objects.exists()


def test_fail_delete_calibration_the_another_user(client_api_auth, calibration, second_user_calibrations):
    '''
    /api/v1/users/<uuid>/calibrations/<uuid> - DELETE
    '''

    second_user_calibration_uuid = second_user_calibrations[0].uuid

    url = resolve_url('api:calibration-read-update-delete', calibration.user.uuid, second_user_calibration_uuid)
    response = client_api_auth.delete(url)

    assert response.status_code == HTTPStatus.NOT_FOUND

    body = response.json()

    assert body['errors'] == MSG_ERROR_RESOURCE

    assert Calibration.objects.count() == 3


def test_update_successful(client_api_auth, form_data, calibration):
    '''
    /api/v1/users/<uuid>/calibrations/<uuid> - PUT
    '''

    update_form_data = form_data.copy()
    update_form_data['syringeActivity'] = 100.0
    update_form_data['calibrationName'] = 'Calibration new'

    url = resolve_url('api:calibration-read-update-delete', calibration.user.uuid, calibration.uuid)

    response = client_api_auth.put(url, data=update_form_data, format='multipart')

    assert response.status_code == HTTPStatus.NO_CONTENT

    calibration_db = Calibration.objects.all().first()

    assert calibration_db.uuid == calibration.uuid
    assert calibration_db.user.uuid == calibration.user.uuid
    assert calibration_db.isotope.name == update_form_data['isotope']
    assert calibration_db.calibration_name == update_form_data['calibrationName']
    assert calibration_db.syringe_activity == update_form_data['syringeActivity']
    assert calibration_db.residual_syringe_activity == update_form_data['residualSyringeActivity']
    assert calibration_db.measurement_datetime == update_form_data['measurementDatetime']
    assert calibration_db.phantom_volume == update_form_data['phantomVolume']
    assert calibration_db.acquisition_time == update_form_data['acquisitionTime']


def test_fail_update_by_wrong_data(client_api_auth, form_data, calibration):
    '''
    /api/v1/users/<uuid>/calibrations/<uuid> - PUT
    '''

    update_form_data = form_data.copy()
    update_form_data['syringeActivity'] = -100.0

    url = resolve_url('api:calibration-read-update-delete', calibration.user.uuid, calibration.uuid)

    response = client_api_auth.put(url, data=update_form_data, format='multipart')

    assert response.status_code == HTTPStatus.BAD_REQUEST

    body = response.json()

    if LANG and USE_I18N:
        expected = ['Certifique-se que atividade da seringa seja maior ou igual a 0.0.']
    else:
        expected = ['Ensure syringe activity value is greater than or equal to 0.0.']

    assert body['errors'] == expected

    calibration_db = Calibration.objects.all().first()

    assert calibration_db.uuid == calibration.uuid
    assert calibration_db.user.uuid == calibration.user.uuid
    assert calibration_db.isotope.name == form_data['isotope']
    assert calibration_db.calibration_name == form_data['calibrationName']
    assert calibration_db.syringe_activity == form_data['syringeActivity']
    assert calibration_db.residual_syringe_activity == form_data['residualSyringeActivity']
    assert calibration_db.measurement_datetime == form_data['measurementDatetime']
    assert calibration_db.phantom_volume == form_data['phantomVolume']
    assert calibration_db.acquisition_time == form_data['acquisitionTime']


def test_fail_update_isotope_invalid(client_api_auth, calibration, form_data):
    '''
    /api/v1/users/<uuid>/calibrations/ - POST
    '''

    url = resolve_url('api:calibration-read-update-delete', calibration.user.uuid, calibration.uuid)

    update_form_data = form_data.copy()
    update_form_data['isotope'] = 'wrong'

    response = client_api_auth.put(url, data=update_form_data, format='multipart')

    assert response.status_code == HTTPStatus.BAD_REQUEST

    body = response.json()

    if LANG == 'pt-br' and USE_I18N:
        expected = ['Isotopo não registrado.']
    else:
        expected = ['Isotope not registered.']

    assert body['errors'] == expected

    calibration_db = Calibration.objects.all().first()

    assert calibration_db.uuid == calibration.uuid
    assert calibration_db.user.uuid == calibration.user.uuid
    assert calibration_db.isotope.name == form_data['isotope']
    assert calibration_db.calibration_name == form_data['calibrationName']
    assert calibration_db.syringe_activity == form_data['syringeActivity']
    assert calibration_db.residual_syringe_activity == form_data['residualSyringeActivity']
    assert calibration_db.measurement_datetime == form_data['measurementDatetime']
    assert calibration_db.phantom_volume == form_data['phantomVolume']
    assert calibration_db.acquisition_time == form_data['acquisitionTime']


def test_fail_update_wrong_calibration_id(client_api_auth, form_data, calibration):
    '''
    /api/v1/users/<uuid>/calibrations/<uuid> - PUT
    '''

    url = resolve_url('api:calibration-read-update-delete', calibration.user.uuid, uuid4())

    response = client_api_auth.put(url, data=form_data, format='multipart')

    assert response.status_code == HTTPStatus.NOT_FOUND

    body = response.json()

    assert body['errors'] == MSG_ERROR_RESOURCE


def test_fail_update_calibration_the_another_user(client_api_auth, form_data, calibration, second_user_calibrations):
    '''
    /api/v1/users/<uuid>/calibrations/<uuid> - PUT
    '''

    second_user_calibration_uuid = second_user_calibrations[0].uuid

    update_form_data = form_data.copy()
    update_form_data['syringeActivity'] = 100.0
    update_form_data['calibrationName'] = 'Calibration new'

    url = resolve_url('api:calibration-read-update-delete', calibration.user.uuid, second_user_calibration_uuid)
    response = client_api_auth.put(url, data=form_data, format='multipart')

    assert response.status_code == HTTPStatus.NOT_FOUND

    body = response.json()

    assert body['errors'] == MSG_ERROR_RESOURCE


def test_update_fail_calibration_name_must_be_unique_per_user(client_api_auth,
                                                              second_calibration,
                                                              form_data,
                                                              second_form_data):
    '''
    /api/v1/users/<uuid>/calibrations/ - POST
    '''

    url = resolve_url('api:calibration-read-update-delete', second_calibration.user.uuid, second_calibration.uuid)

    update_form_data = second_form_data.copy()

    update_form_data['calibrationName'] = form_data['calibrationName']

    response = client_api_auth.put(url, data=update_form_data, format='multipart')

    assert response.status_code == HTTPStatus.BAD_REQUEST

    body = response.json()

    if LANG == 'pt-br' and USE_I18N:
        expected = ['Calibração com esse nome ja existe para este usuário.']
    else:
        expected = ['Calibration with this User and Calibration Name already exists.']

    assert body['errors'] == expected
