from http import HTTPStatus

from django.shortcuts import resolve_url

END_POINT = 'isotopes:isotopes-list'


def test_list_all_isotopes(client_api, isotopes):

    url = resolve_url(END_POINT)

    response = client_api.get(url)

    body = response.json()

    assert response.status_code == HTTPStatus.OK

    isotopes_set = set(map(str, isotopes))

    assert body['count'] == 3
    assert set(body['row']) == isotopes_set


def test_list_dosimetry_isotopes(client_api, isotopes):

    url = resolve_url(END_POINT)

    response = client_api.get(url, data={'q': 'dosimetry'})

    body = response.json()

    assert response.status_code == HTTPStatus.OK

    isotope_set = set(map(str, isotopes[:2]))

    assert body['count'] == 2
    assert set(body['row']) == isotope_set


def test_list_radiosyno_isotopes(client_api, isotopes):

    url = resolve_url(END_POINT)

    response = client_api.get(url, data={'q': 'radiosyno'})

    body = response.json()

    assert response.status_code == HTTPStatus.OK

    isotope_set = set(map(str, isotopes[1:]))

    assert body['count'] == 2
    assert set(body['row']) == isotope_set


def test_not_allowed_method(client_api):

    url = resolve_url(END_POINT)

    resp = client_api.post(url, format='json')
    assert resp.status_code == HTTPStatus.METHOD_NOT_ALLOWED

    resp = client_api.put(url, format='json')
    assert resp.status_code == HTTPStatus.METHOD_NOT_ALLOWED

    resp = client_api.patch(url, format='json')
    assert resp.status_code == HTTPStatus.METHOD_NOT_ALLOWED

    resp = client_api.delete(url, format='json')
    assert resp.status_code == HTTPStatus.METHOD_NOT_ALLOWED
