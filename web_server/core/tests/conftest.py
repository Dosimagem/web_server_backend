import pytest


@pytest.fixture
def api_cnpj_successfull(responses, register_infos):
    return responses.add(
        method='GET',
        url=f'https://brasilapi.com.br/api/cnpj/v1/{register_infos["cnpj"]}',
        status=200,
    )


@pytest.fixture
def api_cnpj_fail(responses, second_register_infos):
    return responses.add(
        method='GET',
        url=f'https://brasilapi.com.br/api/cnpj/v1/{second_register_infos["cnpj"]}',
        status=404,
        json={'message': ['CNPJ 83.398.534/0001-45 não encontrado.']},
    )


def asserts_cookie_tokens(resp):
    access_token = resp.cookies['jwt-access-token']
    refresh_token = resp.cookies['jwt-refresh-token']

    assert '/' == access_token['path']
    assert access_token['httponly']
    assert 'Lax' == access_token['samesite']
    assert 'Sat, 01 Jan 2022 00:15:01 GMT' == access_token['expires']   # 15 minutes

    assert '/api/v1/auth/token/' == refresh_token['path']
    assert refresh_token['httponly']
    assert 'Lax' == refresh_token['samesite']
    assert 'Sat, 01 Jan 2022 01:00:01 GMT' == refresh_token['expires']   # 60 minutes
