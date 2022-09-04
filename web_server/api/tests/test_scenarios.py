from http import HTTPStatus
from django.shortcuts import resolve_url

from web_server.conftest import calibration
from web_server.service.models import Calibration


def test_scenario_read_orders_of_users(client_api, users_and_orders, user, second_user):
    '''
    Order Table:

    ID_USER  Type               Number    price   Status Payment
    1        Dosimetry Clinic     10     10.000   Confirmado
    1        Dosimetry Preclinic   5      5.000   Analise
    2        Dosimetry Clinic      3      3.000   Aguardando pagamento
    '''

    # User 1

    url = resolve_url('api:order-list', user.uuid)
    client_api.credentials(HTTP_AUTHORIZATION='Bearer ' + user.auth_token.key)
    response = client_api.get(url)

    assert response.status_code == HTTPStatus.OK

    user_list_quotes = response.json()['orders']

    assert len(user_list_quotes) == 2

    # order 1 do usuario 1
    q1 = user_list_quotes[0]
    assert q1['serviceName'] == 'Dosimetria Clinica'
    assert q1['quantityOfAnalyzes'] == 10
    assert q1['remainingOfAnalyzes'] == 10
    assert q1['price'] == 10000.00
    assert q1['statusPayment'] == 'Confirmado'
    assert q1['permission']

    # order 2 do usuario 1
    q2 = user_list_quotes[1]
    assert q2['serviceName'] == 'Dosimetria Preclinica'
    assert q2['quantityOfAnalyzes'] == 5
    assert q2['remainingOfAnalyzes'] == 5
    assert q2['price'] == 5000.00
    assert q2['statusPayment'] == 'Analise'
    assert not q2['permission']

    # User 2

    url = resolve_url('api:order-list', second_user.uuid)
    client_api.credentials(HTTP_AUTHORIZATION='Bearer ' + second_user.auth_token.key)
    response = client_api.get(url)

    assert response.status_code == HTTPStatus.OK

    user_list_orders = response.json()['orders']

    assert len(user_list_orders) == 1

    # order 1 do usuario 2
    q1 = user_list_orders[0]
    assert q1['serviceName'] == 'Dosimetria Clinica'
    assert q1['quantityOfAnalyzes'] == 3
    assert q1['remainingOfAnalyzes'] == 3
    assert q1['price'] == 3000.00
    assert q1['statusPayment'] == 'Aguardando pagamento'
    assert not q1['permission']


def test_scenario_calibrations_view(client_api, user, lu_177_and_cu_64, form_data):
    '''
    Isotoper Table:

    ID Name
    1  Lu-177
    2  Cu-64

    User Table:
    ID   EMAIL           ...
    1    test1@email.com

    '''

    # get isotopes

    url = resolve_url('api:isotopes-list')
    response = client_api.get(url)

    assert response.status_code == HTTPStatus.OK

    body = response.json()

    assert body['count'] == 2
    assert body['row'] == [lu_177_and_cu_64[0].name, lu_177_and_cu_64[1].name]

    # Register calibration

    client_api.credentials(HTTP_AUTHORIZATION='Bearer ' + user.auth_token.key)

    url = resolve_url('api:calibration-list-create', user.uuid)
    response = client_api.post(url, data=form_data, format='multipart')

    assert response.status_code == HTTPStatus.CREATED

    form_data['calibrationName'] = 'Calibration 2'
    form_data['isotope'] = 'Cu-64'

    url = resolve_url('api:calibration-list-create', user.uuid)
    response = client_api.post(url, data=form_data, format='multipart')

    assert response.status_code == HTTPStatus.CREATED

    assert Calibration.objects.count() == 2

    # List calibrations

    url = resolve_url('api:calibration-list-create', user.uuid)
    response = client_api.get(url)

    assert response.status_code == HTTPStatus.OK

    body = response.json()

    calibration_list_db = list(Calibration.objects.all())

    assert body['count'] == 2

    # Update

    calibration = calibration_list_db[0]

    form_data['calibrationName'] = 'Calibration 3'

    url = resolve_url('api:calibration-read-update-delete', user.uuid, calibration.uuid)
    response = client_api.put(url, data=form_data, format='multipart')

    assert response.status_code == HTTPStatus.NO_CONTENT

    calibration_update = Calibration.objects.get(id=calibration.id)

    assert calibration_update.calibration_name == form_data['calibrationName']
