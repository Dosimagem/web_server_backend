from http import HTTPStatus
from django.shortcuts import resolve_url


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
    assert q1['service_name'] == 'Dosimetria Clinica'
    assert q1['quantity_of_analyzes'] == 10
    assert q1['remaining_of_analyzes'] == 10
    assert q1['price'] == 10000.00
    assert q1['status_payment'] == 'Confirmado'
    assert q1['permission']

    # order 2 do usuario 1
    q2 = user_list_quotes[1]
    assert q2['service_name'] == 'Dosimetria Preclinica'
    assert q2['quantity_of_analyzes'] == 5
    assert q2['remaining_of_analyzes'] == 5
    assert q2['price'] == 5000.00
    assert q2['status_payment'] == 'Analise'
    assert not q2['permission']

    # User 2

    url = resolve_url('api:order-list', second_user.uuid)
    client_api.credentials(HTTP_AUTHORIZATION='Bearer ' + second_user.auth_token.key)
    response = client_api.get(url)

    assert response.status_code == HTTPStatus.OK

    user_list_quotes = response.json()['orders']

    assert len(user_list_quotes) == 1

    # order 1 do usuario 2
    q1 = user_list_quotes[0]
    assert q1['service_name'] == 'Dosimetria Clinica'
    assert q1['quantity_of_analyzes'] == 3
    assert q1['remaining_of_analyzes'] == 3
    assert q1['price'] == 3000.00
    assert q1['status_payment'] == 'Aguardando pagamento'
    assert not q1['permission']
