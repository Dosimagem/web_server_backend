from http import HTTPStatus

from django.shortcuts import resolve_url

from web_server.service.models import FORMAT_DATE, RadiosynoAnalysis

# /api/v1/users/<uuid>/order/<uuid>/analysis/ - GET


def test_successful(client_api_auth, radiosyno_order, tree_radiosyno_analysis_of_first_user):

    url = resolve_url('service:analysis-list-create', radiosyno_order.user.uuid, radiosyno_order.uuid)
    resp = client_api_auth.get(url)
    body = resp.json()

    assert resp.status_code == HTTPStatus.OK

    analysis_list = body['row']
    analysis_list_db = RadiosynoAnalysis.objects.all()

    assert body['count']
    assert body['count'] == len(analysis_list)

    for analysis_response, analysis_db in zip(analysis_list, analysis_list_db):
        assert analysis_response['id'] == str(analysis_db.uuid)
        assert analysis_response['userId'] == str(analysis_db.order.user.uuid)
        assert analysis_response['orderId'] == str(analysis_db.order.uuid)
        assert analysis_response['status'] == analysis_db.get_status_display()
        assert analysis_response['active'] == analysis_db.active
        assert analysis_response['serviceName'] == analysis_db.order.get_service_name_display()
        assert analysis_response['createdAt'] == analysis_db.created_at.strftime(FORMAT_DATE)
        assert analysis_response['modifiedAt'] == analysis_db.modified_at.strftime(FORMAT_DATE)

        assert analysis_response['isotope'] == analysis_db.isotope.name

        # TODO: Pensar uma forma melhor
        assert analysis_response['imagesUrl'].startswith(f'http://testserver/media/{analysis_db.order.user.id}')

        assert analysis_response['report'] == ''


def test_without_analysis(client_api_auth, clinic_order):

    url = resolve_url('service:analysis-list-create', clinic_order.user.uuid, clinic_order.uuid)
    resp = client_api_auth.get(url)
    body = resp.json()

    assert resp.status_code == HTTPStatus.OK

    assert body['count'] == 0
    assert body['row'] == []
