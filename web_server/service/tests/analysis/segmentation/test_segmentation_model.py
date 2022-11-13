from datetime import datetime

import pytest
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile

from web_server.service.models import Order, SegmentationAnalysis

User = get_user_model()


def test_create(segmentation_analysis):
    assert SegmentationAnalysis.objects.exists()


def test_create_at(segmentation_analysis):
    assert isinstance(segmentation_analysis.created_at, datetime)


def test_modified_at(segmentation_analysis):
    assert isinstance(segmentation_analysis.modified_at, datetime)


def test_delete_user_must_delete_segmentation_analysis(user, segmentation_analysis):
    user.delete()
    assert not SegmentationAnalysis.objects.exists()


def test_delete_segmentation_analysis_must_not_delete_user(user, segmentation_analysis):
    segmentation_analysis.delete()
    assert User.objects.exists()


def test_delete_order_must_delete_segmentation_analysis(segmentation_order, segmentation_analysis):
    segmentation_order.delete()
    assert not SegmentationAnalysis.objects.exists()


def test_delete_segmentation_analysis_must_not_delete_order(segmentation_order, segmentation_analysis):
    segmentation_analysis.delete()
    assert Order.objects.exists()


def test_clinic_dosimetry_one_to_many_relation(user, segmentation_order):

    analysis_1 = SegmentationAnalysis.objects.create(
        order=segmentation_order, analysis_name='Analysis 1', images=ContentFile(b'CT files', name='images.zip')
    )

    analysis_2 = SegmentationAnalysis.objects.create(
        order=segmentation_order, analysis_name='Analysis 2', images=ContentFile(b'CT files', name='images.zip')
    )

    assert segmentation_order.segmentation_analysis.count() == 2

    assert analysis_1.order.user == user
    assert analysis_1.order == segmentation_order

    assert analysis_2.order.user == user
    assert analysis_2.order == segmentation_order


def test_default_values(segmentation_order):

    analysis = SegmentationAnalysis.objects.create(
        order=segmentation_order, analysis_name='Analysis 1', images=ContentFile(b'CT files', name='images.zip')
    )

    assert analysis.status == SegmentationAnalysis.Status.DATA_SENT
    assert analysis.active


def test_str(segmentation_analysis):

    analysis = SegmentationAnalysis.objects.first()

    clinic_id = analysis.order.user.pk
    year = str(analysis.created_at.year)[2:]
    order_id = analysis.order.pk
    analysis_id = analysis.pk
    code = analysis.CODE

    assert str(analysis) == f'{clinic_id:04}.{order_id:04}.{year}/{analysis_id:04}-{code}'


def test_status(segmentation_analysis_info):

    analysis = SegmentationAnalysis(
        **segmentation_analysis_info,
        images=ContentFile(b'CT files', name='images.zip'),
        status='AA',
    )

    with pytest.raises(ValidationError):
        analysis.full_clean()


def test_model_code_and_service_name():

    assert SegmentationAnalysis.CODE == '03'
    assert SegmentationAnalysis.SERVICE_NAME_CODE == 'SQ'


def test_save_with_conclude_status_must_be_report(segmentation_analysis):

    with pytest.raises(ValidationError):
        segmentation_analysis.status = SegmentationAnalysis.Status.CONCLUDED
        segmentation_analysis.full_clean()


def test_order_code(segmentation_analysis):

    clinic_id = segmentation_analysis.order.user.id
    year = str(segmentation_analysis.created_at.year)[2:]
    order_id = segmentation_analysis.order.id
    analysis_id = segmentation_analysis.id
    expected = f'{clinic_id:04}.{order_id:04}.{year}/{analysis_id:04}-03'

    assert expected == segmentation_analysis.code


def test_get_absolute_url(segmentation_analysis):

    user_id = segmentation_analysis.order.user.uuid
    order_id = segmentation_analysis.order.uuid

    expected = f'/api/v1/users/{user_id}/orders/{order_id}/analysis/{segmentation_analysis.uuid}'

    assert expected == segmentation_analysis.get_absolute_url()
