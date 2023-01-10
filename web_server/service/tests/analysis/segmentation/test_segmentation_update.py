from decimal import Decimal
from http import HTTPStatus
from uuid import uuid4

import pytest
from dj_rest_auth.utils import jwt_encode
from django.core.files.base import ContentFile
from django.shortcuts import resolve_url

from web_server.service.models import Order, SegmentationAnalysis


def _verified_unchanged_information_db(clinic_dosimetry):

    analysis_db = SegmentationAnalysis.objects.get(id=clinic_dosimetry.id)

    assert analysis_db.analysis_name == clinic_dosimetry.analysis_name
    assert analysis_db.images.file.read() == clinic_dosimetry.images.file.read()


# /api/v1/users/<uuid>/order/<uuid>/analysis/<uuid> - PUT


def test_successfull(client_api_auth, seg_analysis_update_or_del_is_possible):

    update_form_data = {}

    update_form_data['analysisName'] = 'New analsysis name'
    update_form_data['images'] = ContentFile(b'New File Update', name='images.zip')

    user_uuid = seg_analysis_update_or_del_is_possible.order.user.uuid
    order_uuid = seg_analysis_update_or_del_is_possible.order.uuid
    analysis_uuid = seg_analysis_update_or_del_is_possible.uuid

    url = resolve_url('service:analysis-read-update-delete', user_uuid, order_uuid, analysis_uuid)
    resp = client_api_auth.put(url, data=update_form_data, format='multipart')

    assert resp.status_code == HTTPStatus.NO_CONTENT

    analysis_db = SegmentationAnalysis.objects.get(id=seg_analysis_update_or_del_is_possible.id)

    assert analysis_db.analysis_name == update_form_data['analysisName']
    assert analysis_db.images.file.read() == b'New File Update'
    assert analysis_db.status == SegmentationAnalysis.Status.DATA_SENT


def test_optional_images_successfull(client_api_auth, seg_analysis_update_or_del_is_possible):

    update_form_data = {'analysisName': 'New analsysis name'}

    user_uuid = seg_analysis_update_or_del_is_possible.order.user.uuid
    order_uuid = seg_analysis_update_or_del_is_possible.order.uuid
    analysis_uuid = seg_analysis_update_or_del_is_possible.uuid

    url = resolve_url('service:analysis-read-update-delete', user_uuid, order_uuid, analysis_uuid)
    resp = client_api_auth.put(url, data=update_form_data, format='multipart')

    assert resp.status_code == HTTPStatus.NO_CONTENT

    analysis_db = SegmentationAnalysis.objects.get(id=seg_analysis_update_or_del_is_possible.id)

    assert analysis_db.analysis_name == update_form_data['analysisName']
    assert analysis_db.images.file.read() == seg_analysis_update_or_del_is_possible.images.file.read()
    assert analysis_db.status == SegmentationAnalysis.Status.DATA_SENT


def test_fail_successfull_invalid_status(client_api_auth, segmentation_analysis):
    """
    The analysis must have INVALID_INFOS or DATA_SENT status
    """

    update_form_data = {'analysisName': 'New analsysis name'}

    user_uuid = segmentation_analysis.order.user.uuid
    order_uuid = segmentation_analysis.order.uuid
    analysis_uuid = segmentation_analysis.uuid

    url = resolve_url('service:analysis-read-update-delete', user_uuid, order_uuid, analysis_uuid)
    resp = client_api_auth.put(url, data=update_form_data, format='multipart')
    body = resp.json()

    assert resp.status_code == HTTPStatus.CONFLICT

    expected = [
        'Não foi possivel deletar/atualizar essa análise.'
        ' Apenas análises com os status Informações inválidas ou Dados enviados podem ser deletadas'
    ]

    assert expected == body['errors']

    _verified_unchanged_information_db(segmentation_analysis)


def test_fail_wrong_analysis_id(client_api_auth, seg_analysis_update_or_del_is_possible):

    update_form_data = {'analysisName': 'New analsysis name'}

    user_uuid = seg_analysis_update_or_del_is_possible.order.user.uuid
    order_uuid = seg_analysis_update_or_del_is_possible.order.uuid
    analysis_uuid = uuid4()

    url = resolve_url('service:analysis-read-update-delete', user_uuid, order_uuid, analysis_uuid)
    resp = client_api_auth.put(url, data=update_form_data, format='multipart')
    body = resp.json()

    assert resp.status_code == HTTPStatus.NOT_FOUND
    assert body['errors'] == ['Este usuário não possui este recurso cadastrado.']

    _verified_unchanged_information_db(seg_analysis_update_or_del_is_possible)


def test_fail_wrong_another_order(client_api_auth, user, seg_analysis_update_or_del_is_possible):

    order = Order.objects.create(
        user=user,
        quantity_of_analyzes=10,
        remaining_of_analyzes=10,
        price=Decimal('1000.00'),
        service_name=Order.ServicesName.SEGMENTANTION_QUANTIFICATION.value,
    )

    update_form_data = {}

    update_form_data = {'analysisName': 'New analsysis name'}

    user_uuid = user.uuid
    order_uuid = order.uuid
    analysis_uuid = seg_analysis_update_or_del_is_possible.uuid

    url = resolve_url('service:analysis-read-update-delete', user_uuid, order_uuid, analysis_uuid)
    resp = client_api_auth.put(url, data=update_form_data, format='multipart')
    body = resp.json()

    assert resp.status_code == HTTPStatus.NOT_FOUND
    assert body['errors'] == ['Este usuário não possui este recurso cadastrado.']

    _verified_unchanged_information_db(seg_analysis_update_or_del_is_possible)


def test_fail_wrong_another_user(client_api, second_user, seg_analysis_update_or_del_is_possible):

    update_form_data = {'analysisName': 'New analsysis name'}

    user_uuid = second_user.uuid
    order_uuid = seg_analysis_update_or_del_is_possible.order.uuid
    analysis_uuid = seg_analysis_update_or_del_is_possible.uuid

    url = resolve_url('service:analysis-read-update-delete', user_uuid, order_uuid, analysis_uuid)

    access_token, _ = jwt_encode(second_user)
    client_api.cookies.load({'jwt-access-token': access_token})

    resp = client_api.put(url, data=update_form_data, format='multipart')
    body = resp.json()

    assert resp.status_code == HTTPStatus.NOT_FOUND
    assert body['errors'] == ['Este usuário não possui este recurso cadastrado.']

    _verified_unchanged_information_db(seg_analysis_update_or_del_is_possible)


@pytest.mark.parametrize(
    'field, error',
    [
        ('analysisName', ['analysis_name: Este campo é obrigatório.']),
    ],
)
def test_fail_missing_fields(field, error, client_api_auth, seg_analysis_update_or_del_is_possible):

    update_form_data = {'analysisName': 'New analsysis name'}

    update_form_data.pop(field)

    user_uuid = seg_analysis_update_or_del_is_possible.order.user.uuid
    order_uuid = seg_analysis_update_or_del_is_possible.order.uuid
    analysis_uuid = seg_analysis_update_or_del_is_possible.uuid

    url = resolve_url('service:analysis-read-update-delete', user_uuid, order_uuid, analysis_uuid)

    resp = client_api_auth.put(url, data=update_form_data, format='multipart')

    body = resp.json()

    assert resp.status_code == HTTPStatus.BAD_REQUEST

    assert body['errors'] == error

    _verified_unchanged_information_db(seg_analysis_update_or_del_is_possible)


@pytest.mark.parametrize(
    'field, value, error',
    [
        ('analysisName', '2', ['analysis_name: Certifique-se de que o valor tenha no mínimo 3 caracteres (ele possui 1).']),
    ],
)
def test_fail_invalid_fields(field, value, error, client_api_auth, seg_analysis_update_or_del_is_possible):

    update_form_data = {field: value}

    update_form_data[field] = value

    user_uuid = seg_analysis_update_or_del_is_possible.order.user.uuid
    order_uuid = seg_analysis_update_or_del_is_possible.order.uuid
    analysis_uuid = seg_analysis_update_or_del_is_possible.uuid

    url = resolve_url('service:analysis-read-update-delete', user_uuid, order_uuid, analysis_uuid)

    resp = client_api_auth.put(url, data=update_form_data, format='multipart')

    body = resp.json()

    assert resp.status_code == HTTPStatus.BAD_REQUEST

    assert body['errors'] == error

    _verified_unchanged_information_db(seg_analysis_update_or_del_is_possible)


def test_fail_analysis_name_must_be_unique(client_api_auth, segmentation_order, seg_analysis_update_or_del_is_possible):

    other_analysis = SegmentationAnalysis.objects.create(
        order=segmentation_order,
        analysis_name='Analysis 2',
        images=ContentFile(b'CT e SPET files 1', name='images.zip'),
    )

    update_form_data = {}

    update_form_data = {'analysisName': other_analysis.analysis_name}

    user_uuid = seg_analysis_update_or_del_is_possible.order.user.uuid
    order_uuid = seg_analysis_update_or_del_is_possible.order.uuid
    analysis_uuid = seg_analysis_update_or_del_is_possible.uuid

    url = resolve_url('service:analysis-read-update-delete', user_uuid, order_uuid, analysis_uuid)

    resp = client_api_auth.put(url, data=update_form_data, format='multipart')

    body = resp.json()

    assert resp.status_code == HTTPStatus.BAD_REQUEST

    assert body['errors'] == ['Segmentation Analysis com este Order e Analysis Name já existe.']

    _verified_unchanged_information_db(seg_analysis_update_or_del_is_possible)
