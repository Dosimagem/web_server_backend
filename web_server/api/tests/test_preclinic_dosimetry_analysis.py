from copy import deepcopy
from decimal import Decimal
from http import HTTPStatus
from uuid import uuid4

import pytest
from django.shortcuts import resolve_url

from web_server.service.models import ClinicDosimetryAnalysis, FORMAT_DATE, Order, PreClinicDosimetryAnalysis


def test_create_preclinic_dosimetry(client_api_auth, user, preclinic_order, form_data_preclinic_dosimetry):
    '''
    /api/v1/users/<uuid>/order/<uuid>/analysis/ - POST

    After analyses create order remaining of analyzes must be decreased by one
    '''

    assert not ClinicDosimetryAnalysis.objects.exists()
    assert not PreClinicDosimetryAnalysis.objects.exists()

    assert Order.objects.get(id=preclinic_order.id).remaining_of_analyzes == preclinic_order.remaining_of_analyzes

    url = resolve_url('api:analysis-list-create', user.uuid, preclinic_order.uuid)
    resp = client_api_auth.post(url, data=form_data_preclinic_dosimetry, format='multipart')
    body = resp.json()

    assert resp.status_code == HTTPStatus.CREATED

    assert PreClinicDosimetryAnalysis.objects.exists()
    assert not ClinicDosimetryAnalysis.objects.exists()

    preclinic_dosi_db = PreClinicDosimetryAnalysis.objects.first()

    assert Order.objects.get(id=preclinic_order.id).remaining_of_analyzes == preclinic_order.remaining_of_analyzes - 1

    assert body['id'] == str(preclinic_dosi_db.uuid)
    assert body['userId'] == str(preclinic_dosi_db.user.uuid)
    assert body['orderId'] == str(preclinic_dosi_db.order.uuid)
    assert body['calibrationId'] == str(preclinic_dosi_db.calibration.uuid)
    assert body['status'] == preclinic_dosi_db.get_status_display()
    assert body['active'] == preclinic_dosi_db.active
    assert body['serviceName'] == preclinic_dosi_db.order.get_service_name_display()
    assert body['createdAt'] == preclinic_dosi_db.created_at.strftime(FORMAT_DATE)
    assert body['modifiedAt'] == preclinic_dosi_db.modified_at.strftime(FORMAT_DATE)

    assert body['injectedActivity'] == preclinic_dosi_db.injected_activity
    assert body['analysisName'] == preclinic_dosi_db.analysis_name
    assert body['administrationDatetime'] == preclinic_dosi_db.administration_datetime.strftime(FORMAT_DATE)

    # TODO: gerar a url completa
    assert body['imagesUrl'].startswith(f'http://testserver/media/{preclinic_dosi_db.user.id}/preclinic_dosimetry')


def test_fail_create_preclinic_dosimetry_wrong_administration_datetime(client_api_auth,
                                                                       user,
                                                                       preclinic_order,
                                                                       form_data_preclinic_dosimetry):
    '''
    /api/v1/users/<uuid>/order/<uuid>/analysis/ - POST
    '''

    form_data_preclinic_dosimetry['administration_datetime'] = 'w'

    assert not PreClinicDosimetryAnalysis.objects.exists()

    url = resolve_url('api:analysis-list-create', user.uuid, preclinic_order.uuid)

    resp = client_api_auth.post(url, data=form_data_preclinic_dosimetry, format='multipart')
    body = resp.json()

    assert resp.status_code == HTTPStatus.BAD_REQUEST

    assert not PreClinicDosimetryAnalysis.objects.exists()

    assert body['errors'] == ['Informe uma data/hora válida.']


def test_fail_create_preclinic_dosimetry_injected_activity_must_be_positive(client_api_auth,
                                                                            user,
                                                                            preclinic_order,
                                                                            form_data_preclinic_dosimetry):
    '''
    /api/v1/users/<uuid>/order/<uuid>/analysis/ - POST
    '''

    form_data_preclinic_dosimetry['injectedActivity'] = -form_data_preclinic_dosimetry['injectedActivity']

    assert not PreClinicDosimetryAnalysis.objects.exists()

    url = resolve_url('api:analysis-list-create', user.uuid, preclinic_order.uuid)

    resp = client_api_auth.post(url, data=form_data_preclinic_dosimetry, format='multipart')
    body = resp.json()

    assert resp.status_code == HTTPStatus.BAD_REQUEST

    assert not PreClinicDosimetryAnalysis.objects.exists()

    assert body['errors'] == ['Certifique-se que atividade injetada seja maior ou igual a 0.0.']


def test_fail_create_analisys_name_must_be_unique_per_order(client_api_auth,
                                                            user,
                                                            form_data_preclinic_dosimetry,
                                                            preclinic_dosimetry_info,
                                                            preclinic_dosimetry_file):
    '''
    /api/v1/users/<uuid>/order/<uuid>/analysis/ - POST

    The analysis name must be unique in an order
    '''

    order = preclinic_dosimetry_info['order']

    images = deepcopy(preclinic_dosimetry_file['images'])

    PreClinicDosimetryAnalysis.objects.create(**preclinic_dosimetry_info, **preclinic_dosimetry_file)

    assert PreClinicDosimetryAnalysis.objects.count() == 1

    form_data_preclinic_dosimetry['images'] = images

    url = resolve_url('api:analysis-list-create', user.uuid, order.uuid)
    resp = client_api_auth.post(url, data=form_data_preclinic_dosimetry, format='multipart')
    body = resp.json()

    assert resp.status_code == HTTPStatus.BAD_REQUEST

    assert PreClinicDosimetryAnalysis.objects.count() == 1

    assert body['errors'] == ['Análises com esse nome já existe para esse pedido.']


def test_fail_create_not_have_remaining_of_analyzes(client_api_auth, user, form_data_preclinic_dosimetry):
    '''
    /api/v1/users/<uuid>/order/<uuid>/analysis/ - POST

    All requests for quotas have already been used in use
    '''

    order = Order.objects.create(user=user,
                                 quantity_of_analyzes=3,
                                 remaining_of_analyzes=0,
                                 price=Decimal('3000.00'),
                                 service_name=Order.PRECLINIC_DOSIMETRY,
                                 status_payment=Order.AWAITING_PAYMENT,
                                 permission=True
                                 )

    url = resolve_url('api:analysis-list-create', user.uuid, order.uuid)
    resp = client_api_auth.post(url, data=form_data_preclinic_dosimetry, format='multipart')
    body = resp.json()

    assert resp.status_code == HTTPStatus.CONFLICT

    assert not PreClinicDosimetryAnalysis.objects.exists()

    assert body['errors'] == ['Todas as análises para essa pedido já foram usadas.']


def test_fail_create_preclinic_dosimetry_wrong_calibration_id(client_api_auth,
                                                              user,
                                                              preclinic_order,
                                                              form_data_preclinic_dosimetry):
    '''
    /api/v1/users/<uuid>/order/<uuid>/analysis/ - POST
    '''

    form_data_preclinic_dosimetry['calibrationId'] = uuid4()

    assert not PreClinicDosimetryAnalysis.objects.exists()

    url = resolve_url('api:analysis-list-create', user.uuid, preclinic_order.uuid)

    resp = client_api_auth.post(url, data=form_data_preclinic_dosimetry, format='multipart')

    assert resp.status_code == HTTPStatus.BAD_REQUEST

    assert not PreClinicDosimetryAnalysis.objects.exists()

    body = resp.json()

    assert body['errors'] == ['Calibração com esse id não existe.']


def test_fail_create_preclinic_dosimetry_wrong_(client_api_auth,
                                                user,
                                                preclinic_order,
                                                form_data_preclinic_dosimetry):
    '''
    /api/v1/users/<uuid>/order/<uuid>/analysis/ - POST
    '''

    assert not PreClinicDosimetryAnalysis.objects.exists()

    url = resolve_url('api:analysis-list-create', user.uuid, uuid4())

    resp = client_api_auth.post(url, data=form_data_preclinic_dosimetry, format='multipart')

    assert resp.status_code == HTTPStatus.NOT_FOUND

    assert not PreClinicDosimetryAnalysis.objects.exists()


def test_fail_create_preclinic_dosimetry_order_from_another_user(client_api,
                                                                 user,
                                                                 second_user,
                                                                 tree_orders_of_tow_users,
                                                                 form_data_preclinic_dosimetry):
    '''
    /api/v1/users/<uuid>/order/<uuid>/analysis/ - POST

    User mut be create analysis only in your own orders
    '''

    order_first_user = Order.objects.filter(user=user).first()

    url = resolve_url('api:analysis-list-create', second_user.uuid, order_first_user.uuid)

    client_api.credentials(HTTP_AUTHORIZATION='Bearer ' + second_user.auth_token.key)
    resp = client_api.post(url, data=form_data_preclinic_dosimetry, format='multipart')

    assert resp.status_code == HTTPStatus.NOT_FOUND

    assert not PreClinicDosimetryAnalysis.objects.exists()


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
                                    preclinic_order,
                                    form_data_preclinic_dosimetry):
    '''
     /api/v1/users/<uuid>/order/<uuid>/analysis/ - POST
    '''

    form_data_preclinic_dosimetry.pop(field)

    url = resolve_url('api:analysis-list-create', user.uuid, preclinic_order.uuid)

    resp = client_api_auth.post(url, data=form_data_preclinic_dosimetry, format='multipart')

    body = resp.json()

    assert resp.status_code == HTTPStatus.BAD_REQUEST

    assert not PreClinicDosimetryAnalysis.objects.exists()

    assert body['errors'] == error


def test_list_preclinic_dosimetry(client_api_auth, user, preclinic_order, tree_preclinic_dosimetry_of_first_user):
    '''
    /api/v1/users/<uuid>/order/<uuid>/analysis/ - GET
    '''

    url = resolve_url('api:analysis-list-create', user.uuid, preclinic_order.uuid)
    resp = client_api_auth.get(url)
    body = resp.json()

    assert resp.status_code == HTTPStatus.OK

    analysis_list = body['row']
    analysis_list_db = PreClinicDosimetryAnalysis.objects.all()

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

        assert analysis_response['imagesUrl'].startswith(
            f'http://testserver/media/{analysis_db.user.id}/preclinic_dosimetry'
            )


def test_list_preclinic_dosimetry_without_analysis(client_api_auth, user, preclinic_order):
    '''
    /api/v1/users/<uuid>/order/<uuid>/analysis/ - GET
    '''

    url = resolve_url('api:analysis-list-create', user.uuid, preclinic_order.uuid)
    resp = client_api_auth.get(url)
    body = resp.json()

    assert resp.status_code == HTTPStatus.OK

    assert body['count'] == 0
    assert body['row'] == []
