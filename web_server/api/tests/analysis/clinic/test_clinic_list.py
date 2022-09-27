from http import HTTPStatus

from django.shortcuts import resolve_url

from web_server.service.models import ClinicDosimetryAnalysis, FORMAT_DATE


def test_list_clinic_dosimetry_successful(client_api_auth, user, clinic_order, tree_clinic_dosimetry_of_first_user):
    '''
    /api/v1/users/<uuid>/order/<uuid>/analysis/ - GET
    '''

    url = resolve_url('api:analysis-list-create', user.uuid, clinic_order.uuid)
    resp = client_api_auth.get(url)
    body = resp.json()

    assert resp.status_code == HTTPStatus.OK

    analysis_list = body['row']
    analysis_list_db = ClinicDosimetryAnalysis.objects.all()

    assert body['count']
    assert body['count'] == len(analysis_list)

    for analysis_response, analysis_db in zip(analysis_list, analysis_list_db):
        assert analysis_response['id'] == str(analysis_db.uuid)
        assert analysis_response['userId'] == str(analysis_db.user.uuid)
        assert analysis_response['orderId'] == str(analysis_db.order.uuid)
        assert analysis_response['calibrationId'] == str(analysis_db.calibration.uuid)
        assert analysis_response['status'] == analysis_db.get_status_display()
        assert analysis_response['active'] == analysis_db.active
        assert analysis_response['serviceName'] == analysis_db.order.get_service_name_display()
        assert analysis_response['createdAt'] == analysis_db.created_at.strftime(FORMAT_DATE)
        assert analysis_response['modifiedAt'] == analysis_db.modified_at.strftime(FORMAT_DATE)

        assert analysis_response['injectedActivity'] == analysis_db.injected_activity
        assert analysis_response['analysisName'] == analysis_db.analysis_name
        assert analysis_response['administrationDatetime'] == analysis_db.administration_datetime.strftime(FORMAT_DATE)

        # TODO: Pensar uma forma melhor
        assert analysis_response['imagesUrl'].startswith(
            f'http://testserver/media/{analysis_db.user.id}/clinic_dosimetry'
            )


def test_list_clinic_dosimetry_without_analysis(client_api_auth, user, clinic_order):
    '''
    /api/v1/users/<uuid>/order/<uuid>/analysis/ - GET
    '''

    url = resolve_url('api:analysis-list-create', user.uuid, clinic_order.uuid)
    resp = client_api_auth.get(url)
    body = resp.json()

    assert resp.status_code == HTTPStatus.OK

    assert body['count'] == 0
    assert body['row'] == []
