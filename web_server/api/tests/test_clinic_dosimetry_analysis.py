from http import HTTPStatus
from uuid import uuid4

from django.shortcuts import resolve_url

from web_server.service.models import ClinicDosimetryAnalysis, FORMAT_DATE



def test_create_clinic_dosimetry(client_api_auth, user, order, form_data_clinic_dosimetry):
    '''
    /api/v1/users/<uuid>/order/<uuid>/clinic_dosimetry/ - POST
    '''

    assert not ClinicDosimetryAnalysis.objects.exists()

    url = resolve_url('api:clinic-dosi-list-create', user.uuid, order.uuid)

    resp = client_api_auth.post(url, data=form_data_clinic_dosimetry, format='multipart')

    assert resp.status_code == HTTPStatus.CREATED

    assert ClinicDosimetryAnalysis.objects.exists()

    clinic_dosi_db = ClinicDosimetryAnalysis.objects.first()

    body = resp.json()

    assert body['id'] == str(clinic_dosi_db.uuid)
    assert body['userId'] == str(clinic_dosi_db.user.uuid)
    assert body['orderId'] == str(clinic_dosi_db.order.uuid)
    assert body['calibrationId'] == str(clinic_dosi_db.calibration.uuid)
    assert body['status'] == clinic_dosi_db.get_status_display()
    assert body['images'] == clinic_dosi_db.images.url # TODO: gerar a url completa
    assert body['active'] == clinic_dosi_db.active
    assert body['createdAt'] == clinic_dosi_db.created_at.strftime(FORMAT_DATE)
    assert body['modifiedAt'] == clinic_dosi_db.modified_at.strftime(FORMAT_DATE)


def test_fail_create_clinic_dosimetry_missing_calibration_id(client_api_auth, user, order, form_data_clinic_dosimetry):
    '''
    /api/v1/users/<uuid>/order/<uuid>/clinic_dosimetry/ - POST
    '''

    form_data_clinic_dosimetry.pop('calibration_id')

    assert not ClinicDosimetryAnalysis.objects.exists()

    url = resolve_url('api:clinic-dosi-list-create', user.uuid, order.uuid)

    resp = client_api_auth.post(url, data=form_data_clinic_dosimetry, format='multipart')

    assert resp.status_code == HTTPStatus.BAD_REQUEST

    assert not ClinicDosimetryAnalysis.objects.exists()

    body = resp.json()

    assert body['errors'] == ['O campo id de calibração é obrigatório.']


def test_fail_create_clinic_dosimetry_wrong_calibration_id(client_api_auth, user, order, form_data_clinic_dosimetry):
    '''
    /api/v1/users/<uuid>/order/<uuid>/clinic_dosimetry/ - POST
    '''

    form_data_clinic_dosimetry['calibration_id'] = uuid4()

    assert not ClinicDosimetryAnalysis.objects.exists()

    url = resolve_url('api:clinic-dosi-list-create', user.uuid, order.uuid)

    resp = client_api_auth.post(url, data=form_data_clinic_dosimetry, format='multipart')

    assert resp.status_code == HTTPStatus.BAD_REQUEST

    assert not ClinicDosimetryAnalysis.objects.exists()

    body = resp.json()

    assert body['errors'] == ['Calibração com esse id não existe.']


def test_fail_create_clinic_dosimetry_wrong_order_id(client_api_auth, user, order, form_data_clinic_dosimetry):
    '''
    /api/v1/users/<uuid>/order/<uuid>/clinic_dosimetry/ - POST
    '''

    assert not ClinicDosimetryAnalysis.objects.exists()

    url = resolve_url('api:clinic-dosi-list-create', user.uuid, uuid4())

    resp = client_api_auth.post(url, data=form_data_clinic_dosimetry, format='multipart')

    assert resp.status_code == HTTPStatus.NOT_FOUND

    assert not ClinicDosimetryAnalysis.objects.exists()


# Fazer teste o com order valida de outro usuario
# Fazer o teste com o token de um usuario diferente