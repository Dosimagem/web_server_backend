from copy import deepcopy
from http import HTTPStatus

from django.shortcuts import resolve_url
from django.core.files.base import ContentFile

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

    body = response.json()

    user_list_quotes = body['row']

    assert body['count'] == 2

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

    body = response.json()

    user_list_orders = body['row']

    assert body['count'] == 1

    # order 1 do usuario 2
    q1 = user_list_orders[0]
    assert q1['serviceName'] == 'Dosimetria Clinica'
    assert q1['quantityOfAnalyzes'] == 3
    assert q1['remainingOfAnalyzes'] == 3
    assert q1['price'] == 3000.00
    assert q1['statusPayment'] == 'Aguardando pagamento'
    assert not q1['permission']


def test_scenario_calibrations_view(client_api, user, second_user, lu_177_and_cu_64, form_data):
    '''
    Isotoper Table:

    ID Name
    1  Lu-177
    2  Cu-64

    User Table:
    ID   EMAIL           ...
    1    test1@email.com
    2    test2@email.com

    '''

    # get isotopes

    url = resolve_url('api:isotopes-list')
    response = client_api.get(url)

    assert response.status_code == HTTPStatus.OK

    body = response.json()

    assert body['count'] == 2
    assert body['row'] == [lu_177_and_cu_64[0].name, lu_177_and_cu_64[1].name]

    # Register 2 calibration for user 1

    images = deepcopy(form_data['images'])  # the file is consumed

    client_api.credentials(HTTP_AUTHORIZATION='Bearer ' + user.auth_token.key)

    form_data['calibrationName'] = 'Calibration 1 of user 1'

    current_user = user
    client_api.credentials(HTTP_AUTHORIZATION='Bearer ' + current_user.auth_token.key)
    url = resolve_url('api:calibration-list-create', current_user.uuid)
    response = client_api.post(url, data=form_data, format='multipart')

    assert response.status_code == HTTPStatus.CREATED

    form_data['calibrationName'] = 'Calibration 2 of user 2'
    form_data['isotope'] = 'Cu-64'
    form_data['images'] = deepcopy(images)

    url = resolve_url('api:calibration-list-create', current_user.uuid)
    response = client_api.post(url, data=form_data, format='multipart')

    assert response.status_code == HTTPStatus.CREATED

    assert Calibration.objects.count() == 2

    # Register 1 calibration for user 2

    form_data['images'] = deepcopy(images)

    current_user = second_user
    client_api.credentials(HTTP_AUTHORIZATION='Bearer ' + current_user.auth_token.key)
    url = resolve_url('api:calibration-list-create', current_user.uuid)
    response = client_api.post(url, data=form_data, format='multipart')

    assert response.status_code == HTTPStatus.CREATED

    # List calibrations use 1

    current_user = user
    client_api.credentials(HTTP_AUTHORIZATION='Bearer ' + current_user.auth_token.key)
    url = resolve_url('api:calibration-list-create', current_user.uuid)
    response = client_api.get(url)

    assert response.status_code == HTTPStatus.OK

    body = response.json()

    assert body['count'] == 2  # User 1

    # List calibrations of use 2

    current_user = second_user
    client_api.credentials(HTTP_AUTHORIZATION='Bearer ' + current_user.auth_token.key)
    url = resolve_url('api:calibration-list-create', current_user.uuid)
    response = client_api.get(url)

    assert response.status_code == HTTPStatus.OK

    body = response.json()

    assert body['count'] == 1  # User 2

    # Update the 1th calibration

    calibration = Calibration.objects.filter(user=user).first()

    form_data['calibrationName'] = 'Calibration 3 of User 1'
    form_data['images'] = deepcopy(images)

    current_user = user
    client_api.credentials(HTTP_AUTHORIZATION='Bearer ' + current_user.auth_token.key)
    url = resolve_url('api:calibration-read-update-delete', current_user.uuid, calibration.uuid)
    response = client_api.put(url, data=form_data, format='multipart')

    assert response.status_code == HTTPStatus.NO_CONTENT

    calibration_update = Calibration.objects.get(id=calibration.id)

    assert calibration_update.calibration_name == form_data['calibrationName']

    # Delete the 1th calibration if user 1

    current_user = user
    client_api.credentials(HTTP_AUTHORIZATION='Bearer ' + current_user.auth_token.key)
    url = resolve_url('api:calibration-read-update-delete', current_user.uuid, calibration.uuid)
    response = client_api.delete(url)

    assert response.status_code == HTTPStatus.OK

    assert not Calibration.objects.filter(id=calibration.id)

    # List calibrations use 1 afeter delete

    current_user = user
    client_api.credentials(HTTP_AUTHORIZATION='Bearer ' + current_user.auth_token.key)
    url = resolve_url('api:calibration-list-create', current_user.uuid)
    response = client_api.get(url)

    assert response.status_code == HTTPStatus.OK

    body = response.json()

    assert body['count'] == 1  # User 1


def test_scenario_update_calibration_images(client_api, user, form_data, calibration_with_images):
    '''
    Calibration Already file
    '''

    cali_db = Calibration.objects.first()

    fp = deepcopy(cali_db.images)

    assert fp.read() == b'file_content'

    form_data['images'] = ContentFile(b'New calibration file', name='images.zip')

    client_api.credentials(HTTP_AUTHORIZATION='Bearer ' + user.auth_token.key)
    url = resolve_url('api:calibration-read-update-delete', user.uuid, calibration_with_images.uuid)
    response = client_api.put(url, data=form_data, format='multipart')

    assert response.status_code == HTTPStatus.NO_CONTENT

    cali_db = Calibration.objects.first()

    fp = deepcopy(cali_db.images)

    assert fp.read() == b'New calibration file'
