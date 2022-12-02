from http import HTTPStatus


def test_healty(client_api):

    resp = client_api.get('/api/v1/health/')

    assert resp.status_code == HTTPStatus.NO_CONTENT
