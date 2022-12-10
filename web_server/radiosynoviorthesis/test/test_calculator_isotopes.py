from http import HTTPStatus

from django.shortcuts import resolve_url

END_POINT = 'radiosyn:isotopes'


def test_calculator_isotopes(client_api):

    url = resolve_url(END_POINT)

    resp = client_api.get(url)

    assert resp.status_code == HTTPStatus.OK

    expected = ['Y-90', 'P-32', 'Re-188', 'Re-186', 'Sm-153', 'Lu-177']

    body = resp.json()

    assert len(expected) == body['count']
    assert expected == body['row']


def test_read_not_allowed_method(client_api):

    url = resolve_url(END_POINT)

    resp = client_api.post(url, format='json')
    assert resp.status_code == HTTPStatus.METHOD_NOT_ALLOWED

    resp = client_api.put(url, format='json')
    assert resp.status_code == HTTPStatus.METHOD_NOT_ALLOWED

    resp = client_api.patch(url, format='json')
    assert resp.status_code == HTTPStatus.METHOD_NOT_ALLOWED

    resp = client_api.delete(url, format='json')
    assert resp.status_code == HTTPStatus.METHOD_NOT_ALLOWED
