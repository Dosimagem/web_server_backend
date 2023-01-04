from http import HTTPStatus

from django.shortcuts import resolve_url

from web_server.service.views.isotopes import _isotope_to_list


def test_list_isotopes(client_api, lu_177):

    url = resolve_url('service:isotopes-list')

    response = client_api.get(url)

    body = response.json()

    assert response.status_code == HTTPStatus.OK

    isotope_db_list = _isotope_to_list()

    assert body['count'] == 1
    assert body['row'] == isotope_db_list
