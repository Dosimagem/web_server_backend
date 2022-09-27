from copy import deepcopy
from decimal import Decimal
from http import HTTPStatus
from uuid import uuid4

import pytest
from django.shortcuts import resolve_url

from web_server.service.models import ClinicDosimetryAnalysis, FORMAT_DATE, Order, PreClinicDosimetryAnalysis


# POST

def test_create_clinic_dosimetry_successful(client_api_auth, user, clinic_order, form_data_clinic_dosimetry):
    '''
    /api/v1/users/<uuid>/order/<uuid>/analysis/ - POST

    After analyses create order remaining of analyzes must be decreased by one
    '''

    assert not ClinicDosimetryAnalysis.objects.exists()
    assert not PreClinicDosimetryAnalysis.objects.exists()

    assert Order.objects.get(id=clinic_order.id).remaining_of_analyzes == clinic_order.remaining_of_analyzes

    url = resolve_url('api:analysis-list-create', user.uuid, clinic_order.uuid)
    resp = client_api_auth.post(url, data=form_data_clinic_dosimetry, format='multipart')
    body = resp.json()

    assert resp.status_code == HTTPStatus.CREATED

    assert not PreClinicDosimetryAnalysis.objects.exists()
    assert ClinicDosimetryAnalysis.objects.exists()

    clinic_dosi_db = ClinicDosimetryAnalysis.objects.first()

    assert Order.objects.get(id=clinic_order.id).remaining_of_analyzes == clinic_order.remaining_of_analyzes - 1

    assert body['id'] == str(clinic_dosi_db.uuid)
    assert body['userId'] == str(clinic_dosi_db.user.uuid)
    assert body['orderId'] == str(clinic_dosi_db.order.uuid)
    assert body['calibrationId'] == str(clinic_dosi_db.calibration.uuid)
    assert body['status'] == clinic_dosi_db.get_status_display()
    assert body['active'] == clinic_dosi_db.active
    assert body['serviceName'] == clinic_dosi_db.order.get_service_name_display()
    assert body['createdAt'] == clinic_dosi_db.created_at.strftime(FORMAT_DATE)
    assert body['modifiedAt'] == clinic_dosi_db.modified_at.strftime(FORMAT_DATE)

    assert body['injectedActivity'] == clinic_dosi_db.injected_activity
    assert body['analysisName'] == clinic_dosi_db.analysis_name
    assert body['administrationDatetime'] == clinic_dosi_db.administration_datetime.strftime(FORMAT_DATE)

    # TODO: Pensar uma forma melhor
    assert body['imagesUrl'].startswith(f'http://testserver/media/{clinic_dosi_db.user.id}/clinic_dosimetry')


def test_fail_create_clinic_dosimetry_wrong_administration_datetime(client_api_auth,
                                                                    user,
                                                                    clinic_order,
                                                                    form_data_clinic_dosimetry):
    '''
    /api/v1/users/<uuid>/order/<uuid>/analysis/ - POST
    '''

    form_data_clinic_dosimetry['administrationDatetime'] = 'w'

    assert not ClinicDosimetryAnalysis.objects.exists()

    url = resolve_url('api:analysis-list-create', user.uuid, clinic_order.uuid)

    resp = client_api_auth.post(url, data=form_data_clinic_dosimetry, format='multipart')
    body = resp.json()

    assert resp.status_code == HTTPStatus.BAD_REQUEST

    assert not ClinicDosimetryAnalysis.objects.exists()

    assert body['errors'] == ['Informe uma data/hora válida.']


def test_fail_create_preclinic_dosimetry_injected_activity_must_be_positive(client_api_auth,
                                                                            user,
                                                                            clinic_order,
                                                                            form_data_clinic_dosimetry):
    '''
    /api/v1/users/<uuid>/order/<uuid>/analysis/ - POST
    '''

    form_data_clinic_dosimetry['injectedActivity'] = -form_data_clinic_dosimetry['injectedActivity']

    assert not ClinicDosimetryAnalysis.objects.exists()

    url = resolve_url('api:analysis-list-create', user.uuid, clinic_order.uuid)

    resp = client_api_auth.post(url, data=form_data_clinic_dosimetry, format='multipart')
    body = resp.json()

    assert resp.status_code == HTTPStatus.BAD_REQUEST

    assert not ClinicDosimetryAnalysis.objects.exists()

    assert body['errors'] == ['Certifique-se que atividade injetada seja maior ou igual a 0.0.']


def test_fail_create_analisys_name_must_be_unique_per_order(client_api_auth,
                                                            user,
                                                            form_data_clinic_dosimetry,
                                                            clinic_dosimetry_info,
                                                            clinic_dosimetry_file):
    '''
    /api/v1/users/<uuid>/order/<uuid>/analysis/ - POST

    The analysis name must be unique in an order
    '''

    order = clinic_dosimetry_info['order']

    images = deepcopy(clinic_dosimetry_file['images'])

    ClinicDosimetryAnalysis.objects.create(**clinic_dosimetry_info, **clinic_dosimetry_file)

    assert ClinicDosimetryAnalysis.objects.count() == 1

    form_data_clinic_dosimetry['images'] = images

    url = resolve_url('api:analysis-list-create', user.uuid, order.uuid)
    resp = client_api_auth.post(url, data=form_data_clinic_dosimetry, format='multipart')
    body = resp.json()

    assert resp.status_code == HTTPStatus.BAD_REQUEST

    assert ClinicDosimetryAnalysis.objects.count() == 1

    assert body['errors'] == ['Análises com esse nome já existe para esse pedido.']


def test_fail_create_not_have_remaining_of_analyzes(client_api_auth, user, form_data_clinic_dosimetry):
    '''
    /api/v1/users/<uuid>/order/<uuid>/analysis/ - POST

    All requests for quotas have already been used in use
    '''

    order = Order.objects.create(user=user,
                                 quantity_of_analyzes=3,
                                 remaining_of_analyzes=0,
                                 price=Decimal('3000.00'),
                                 service_name=Order.CLINIC_DOSIMETRY,
                                 status_payment=Order.AWAITING_PAYMENT,
                                 permission=True
                                 )

    url = resolve_url('api:analysis-list-create', user.uuid, order.uuid)
    resp = client_api_auth.post(url, data=form_data_clinic_dosimetry, format='multipart')
    body = resp.json()

    assert resp.status_code == HTTPStatus.CONFLICT

    assert not ClinicDosimetryAnalysis.objects.exists()

    assert body['errors'] == ['Todas as análises para essa pedido já foram usadas.']


def test_fail_create_clinic_dosimetry_missing_calibration_id(client_api_auth,
                                                             user,
                                                             clinic_order,
                                                             form_data_clinic_dosimetry):
    '''
    /api/v1/users/<uuid>/order/<uuid>/analysis/ - POST
    '''

    form_data_clinic_dosimetry.pop('calibrationId')

    assert not ClinicDosimetryAnalysis.objects.exists()

    url = resolve_url('api:analysis-list-create', user.uuid, clinic_order.uuid)

    resp = client_api_auth.post(url, data=form_data_clinic_dosimetry, format='multipart')

    assert resp.status_code == HTTPStatus.BAD_REQUEST

    assert not ClinicDosimetryAnalysis.objects.exists()

    body = resp.json()

    assert body['errors'] == ['O campo id de calibração é obrigatório.']


def test_fail_create_clinic_dosimetry_wrong_calibration_id(client_api_auth,
                                                           user,
                                                           clinic_order,
                                                           form_data_clinic_dosimetry):
    '''
    /api/v1/users/<uuid>/order/<uuid>/analysis/ - POST
    '''

    form_data_clinic_dosimetry['calibrationId'] = uuid4()

    assert not ClinicDosimetryAnalysis.objects.exists()

    url = resolve_url('api:analysis-list-create', user.uuid, clinic_order.uuid)

    resp = client_api_auth.post(url, data=form_data_clinic_dosimetry, format='multipart')

    assert resp.status_code == HTTPStatus.BAD_REQUEST

    assert not ClinicDosimetryAnalysis.objects.exists()

    body = resp.json()

    assert body['errors'] == ['Calibração com esse id não existe para esse usuário.']


def test_fail_create_clinic_dosimetry_wrong_order_id(client_api_auth, user, clinic_order, form_data_clinic_dosimetry):
    '''
    /api/v1/users/<uuid>/order/<uuid>/analysis/ - POST
    '''

    assert not ClinicDosimetryAnalysis.objects.exists()

    url = resolve_url('api:analysis-list-create', user.uuid, uuid4())

    resp = client_api_auth.post(url, data=form_data_clinic_dosimetry, format='multipart')

    assert resp.status_code == HTTPStatus.NOT_FOUND

    assert not ClinicDosimetryAnalysis.objects.exists()


def test_fail_create_clinic_dosimetry_with_order_from_another_user(client_api_auth,
                                                                   user,
                                                                   second_user,
                                                                   tree_orders_of_tow_users,
                                                                   form_data_clinic_dosimetry):
    '''
    /api/v1/users/<uuid>/order/<uuid>/analysis/ - POST

    User must be create analysis only in your own orders
    '''

    order_second_user = Order.objects.filter(user=second_user).first()

    url = resolve_url('api:analysis-list-create', user.uuid, order_second_user.uuid)

    resp = client_api_auth.post(url, data=form_data_clinic_dosimetry, format='multipart')

    assert resp.status_code == HTTPStatus.NOT_FOUND

    assert not ClinicDosimetryAnalysis.objects.exists()


def test_fail_create_clinic_dosimetry_whith_calibration_of_another_user(client_api_auth,
                                                                        user,
                                                                        clinic_order,
                                                                        second_user_calibrations,
                                                                        form_data_clinic_dosimetry):
    '''
    /api/v1/users/<uuid>/order/<uuid>/analysis/ - POST
    '''

    assert not ClinicDosimetryAnalysis.objects.exists()

    form_data_clinic_dosimetry['calibrationId'] = second_user_calibrations[0].uuid

    url = resolve_url('api:analysis-list-create', user.uuid, clinic_order.uuid)
    resp = client_api_auth.post(url, data=form_data_clinic_dosimetry, format='multipart')
    body = resp.json()

    assert resp.status_code == HTTPStatus.BAD_REQUEST

    assert not ClinicDosimetryAnalysis.objects.exists()

    assert body['errors'] == ['Calibração com esse id não existe para esse usuário.']


@pytest.mark.parametrize('field, error', [
    ('calibrationId', ['O campo id de calibração é obrigatório.']),
    ('images', ['O campo imagens é obrigatório.']),
    ('analysisName', ['O campo nome da análise é obrigatório.']),
    ('injectedActivity', ['O campo atividade injetada é obrigatório.']),
    ('administrationDatetime', ['O campo hora e data de adminstração é obrigatório.']),
    ])
def test_fail_create_missing_fields(field,
                                    error,
                                    client_api_auth,
                                    user,
                                    clinic_order,
                                    form_data_clinic_dosimetry):
    '''
     /api/v1/users/<uuid>/order/<uuid>/analysis/ - POST
    '''

    form_data_clinic_dosimetry.pop(field)

    url = resolve_url('api:analysis-list-create', user.uuid, clinic_order.uuid)

    resp = client_api_auth.post(url, data=form_data_clinic_dosimetry, format='multipart')

    body = resp.json()

    assert resp.status_code == HTTPStatus.BAD_REQUEST

    assert not ClinicDosimetryAnalysis.objects.exists()

    assert body['errors'] == error