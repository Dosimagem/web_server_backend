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
