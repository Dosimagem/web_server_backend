from copy import deepcopy
from decimal import Decimal
from http import HTTPStatus
from uuid import uuid4

import pytest
from django.shortcuts import resolve_url

from web_server.service.models import ClinicDosimetryAnalysis, FORMAT_DATE, Order, PreClinicDosimetryAnalysis
from web_server.api.views.errors_msg import MSG_ERROR_TOKEN_USER


def test_list_create_analysis_not_allowed_method(client_api_auth, user, clinic_order):
    '''
    /api/v1/users/<uuid>/order/<uuid>/analysis/ - GET, POST
    '''

    url = resolve_url('api:analysis-list-create', user.uuid, clinic_order.uuid)

    resp = client_api_auth.put(url)
    assert resp.status_code == HTTPStatus.METHOD_NOT_ALLOWED

    resp = client_api_auth.patch(url)
    assert resp.status_code == HTTPStatus.METHOD_NOT_ALLOWED

    resp = client_api_auth.delete(url)
    assert resp.status_code == HTTPStatus.METHOD_NOT_ALLOWED


def test_list_create_token_view_and_user_id_dont_match(client_api, user, second_user, clinic_order):
    '''
    /api/v1/users/<uuid>/order/<uuid>/analysis/ - GET, POST
    The token does not belong to the user
    '''

    client_api.credentials(HTTP_AUTHORIZATION='Bearer ' + user.auth_token.key)

    url = resolve_url('api:analysis-list-create', second_user.uuid, clinic_order.uuid)
    response = client_api.get(url)

    assert response.status_code == HTTPStatus.UNAUTHORIZED

    body = response.json()

    assert body['errors'] == MSG_ERROR_TOKEN_USER


def test_create_clinic_dosimetry(client_api_auth, user, clinic_order, form_data_clinic_dosimetry):
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


def test_list_clinic_dosimetry(client_api_auth, user, clinic_order, tree_clinic_dosimetry_of_first_user):
    '''
    /api/v1/users/<uuid>/order/<uuid>/analysis/ - GET
    '''

    url = resolve_url('api:analysis-list-create', user.uuid, clinic_order.uuid)
    resp = client_api_auth.get(url)
    body = resp.json()

    assert resp.status_code == HTTPStatus.OK

    analysis_list = body['row']
    analysis_list_db = ClinicDosimetryAnalysis.objects.all()

    assert body['count']
    assert body['count'] == len(analysis_list)

    for analysis_response, analysis_db in zip(analysis_list, analysis_list_db):
        assert analysis_response['id'] == str(analysis_db.uuid)
        assert analysis_response['userId'] == str(analysis_db.user.uuid)
        assert analysis_response['orderId'] == str(analysis_db.order.uuid)
        assert analysis_response['calibrationId'] == str(analysis_db.calibration.uuid)
        assert analysis_response['status'] == analysis_db.get_status_display()
        assert analysis_response['active'] == analysis_db.active
        assert analysis_response['serviceName'] == analysis_db.order.get_service_name_display()
        assert analysis_response['createdAt'] == analysis_db.created_at.strftime(FORMAT_DATE)
        assert analysis_response['modifiedAt'] == analysis_db.modified_at.strftime(FORMAT_DATE)

        assert analysis_response['injectedActivity'] == analysis_db.injected_activity
        assert analysis_response['analysisName'] == analysis_db.analysis_name
        assert analysis_response['administrationDatetime'] == analysis_db.administration_datetime.strftime(FORMAT_DATE)

        # TODO: Pensar uma forma melhor
        assert analysis_response['imagesUrl'].startswith(
            f'http://testserver/media/{analysis_db.user.id}/clinic_dosimetry'
            )


def test_list_clinic_dosimetry_without_analysis(client_api_auth, user, clinic_order):
    '''
    /api/v1/users/<uuid>/order/<uuid>/analysis/ - GET
    '''

    url = resolve_url('api:analysis-list-create', user.uuid, clinic_order.uuid)
    resp = client_api_auth.get(url)
    body = resp.json()

    assert resp.status_code == HTTPStatus.OK

    assert body['count'] == 0
    assert body['row'] == []
