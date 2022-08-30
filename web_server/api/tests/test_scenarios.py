# import pytest
# from decimal import Decimal

# from rest_framework.authtoken.models import Token

# from web_server.service.models import UserQuota
# from web_server.core.models import UserProfile
# from web_server.core.models import CustomUser as User
from http import HTTPStatus
from django.shortcuts import resolve_url


def test_scenario_read_quotas_of_users(client_api, users_and_quotas, user, second_user):
    '''
    UserQuota Table:

    ID_USER  Type               Number    price   Status Payment
    1        Dosimetry Clinic     10     10.000   Confirmado
    1        Dosimetry Preclinic   5      5.000   Analise
    2        Dosimetry Clinic      3      3.000   Aguardando pagamento
    '''

    # User 1

    url = resolve_url('api:create-list', user.uuid)
    client_api.credentials(HTTP_AUTHORIZATION='Bearer ' + user.auth_token.key)
    response = client_api.get(url)

    user_list_quotes = response.json()['quotas']

    assert len(user_list_quotes) == 2

    # quota 1 do usuario 1
    q1 = user_list_quotes[0]
    assert q1['service_type'] == 'Dosimetria Clinica'
    assert q1['amount'] == 10
    assert q1['price'] == 10000.00
    assert q1['status_payment'] == 'Confirmado'

    # quota 2 do usuario 1
    q2 = user_list_quotes[1]
    assert q2['service_type'] == 'Dosimetria Preclinica'
    assert q2['amount'] == 5
    assert q2['price'] == 5000.00
    assert q2['status_payment'] == 'Analise'

    # User 2

    url = resolve_url('api:create-list', second_user.uuid)
    client_api.credentials(HTTP_AUTHORIZATION='Bearer ' + second_user.auth_token.key)
    response = client_api.get(url)
    user_list_quotes = response.json()['quotas']

    assert len(user_list_quotes) == 1

    # quota 1 do usuario 2
    q1 = user_list_quotes[0]
    assert q1['service_type'] == 'Dosimetria Clinica'
    assert q1['amount'] == 3
    assert q1['price'] == 3000.00
    assert q1['status_payment'] == 'Aguardando pagamento'


def test_scenario_read_update_amount(client_api, users_and_quotas, user):
    '''
    UserQuota Table:

    ID_USER  Type               Number    price   Status Payment
    1        Dosimetry Clinic     10     10.000   Confirmado
    1        Dosimetry Preclinic   5      5.000   Analise
    2        Dosimetry Clinic      3      3.000   Aguardando pagamento

    1) Get quotas list of user 1
    2) Update amount second row of user 1
    3) Read this quota again

    '''

    # 1) Step 1

    client_api.credentials(HTTP_AUTHORIZATION='Bearer ' + user.auth_token.key)

    url = resolve_url('api:create-list', user.uuid)
    response = client_api.get(url)

    assert response.status_code == HTTPStatus.OK

    user_list_quotes = response.json()['quotas']

    # quota 1 do usuario 2
    q = user_list_quotes[1]
    assert q['service_type'] == 'Dosimetria Preclinica'
    assert q['amount'] == 5
    assert q['price'] == 5000.00
    assert q['status_payment'] == 'Analise'

    # 2) Step 2

    url = resolve_url('api:read-patch-delete', q['user_id'], q['id'])

    response = client_api.patch(url, data={'amount': 9})
    assert response.status_code == HTTPStatus.NO_CONTENT

    # 3) Step 3

    response = client_api.get(url)
    assert response.status_code == HTTPStatus.OK

    body = response.json()

    assert body['service_type'] == 'Dosimetria Preclinica'
    assert body['amount'] == 9
    assert body['price'] == 5000.00
    assert body['status_payment'] == 'Analise'
