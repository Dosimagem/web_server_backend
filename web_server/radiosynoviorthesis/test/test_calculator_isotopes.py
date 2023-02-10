from http import HTTPStatus

from django.shortcuts import resolve_url

from web_server.service.models import IsotopeRadiosyno

END_POINT = 'radiosyn:isotopes'


def test_calculator_isotopes(client_api, db):

    IsotopeRadiosyno.objects.create(name='Y-90')
    IsotopeRadiosyno.objects.create(name='L-177')

    url = resolve_url(END_POINT)

    resp = client_api.get(url)

    assert resp.status_code == HTTPStatus.OK

    expected = ['L-177', 'Y-90']
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
