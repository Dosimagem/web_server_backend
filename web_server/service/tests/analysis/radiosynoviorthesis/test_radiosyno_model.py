from datetime import datetime

import pytest
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile

from web_server.service.models import Order, RadiosynoAnalysis

User = get_user_model()


def test_create(radiosyno_analysis):
    assert RadiosynoAnalysis.objects.exists()


def test_create_at(radiosyno_analysis):
    assert isinstance(radiosyno_analysis.created_at, datetime)


def test_modified_at(radiosyno_analysis):
    assert isinstance(radiosyno_analysis.modified_at, datetime)


def test_delete_user_must_delete_radiosyno_analysis(user, radiosyno_analysis):
    user.delete()
    assert not RadiosynoAnalysis.objects.exists()


def test_delete_radiosyno_must_not_delete_user(user, radiosyno_analysis):
    radiosyno_analysis.delete()
    assert User.objects.exists()


def test_delete_order_must_delete_radiosyno_analysis(radiosyno_order, radiosyno_analysis):
    radiosyno_order.delete()
    assert not RadiosynoAnalysis.objects.exists()


def test_delete_radiosyno_analysis_must_not_delete_order(radiosyno_order, radiosyno_analysis):
    radiosyno_analysis.delete()
    assert Order.objects.exists()


def test_radiosyno_analysis_one_to_many_relation(user, radiosyno_order, lu_177):
    analyis_1 = RadiosynoAnalysis.objects.create(
        order=radiosyno_order,
        analysis_name='Analysis 1',
        isotope=lu_177,
        images=ContentFile(b'CT e SPET files', name='images.zip'),
    )

    analyis_2 = RadiosynoAnalysis.objects.create(
        order=radiosyno_order,
        analysis_name='Analysis 2',
        isotope=lu_177,
        images=ContentFile(b'CT e SPET files', name='images.zip'),
    )

    assert radiosyno_order.radiosyno_analysis.count() == 2

    assert analyis_1.order == radiosyno_order
    assert analyis_2.order == radiosyno_order


def test_default_values(user, radiosyno_order, lu_177):

    analyis = RadiosynoAnalysis.objects.create(
        order=radiosyno_order,
        isotope=lu_177,
        analysis_name='Analysis 1',
        images=ContentFile(b'CT e SPET files', name='images.zip'),
    )

    assert analyis.status == RadiosynoAnalysis.DATA_SENT
    assert analyis.active


def test_str(radiosyno_analysis):

    analysis = RadiosynoAnalysis.objects.first()

    clinic_id = analysis.order.user.pk
    isotope = analysis.isotope
    year = str(analysis.created_at.year)[2:]
    order_id = analysis.order.pk
    analysis_id = analysis.pk
    code = analysis.CODE

    assert str(analysis) == f'{clinic_id:04}.{order_id:04}.{isotope}.{year}/{analysis_id:04}-{code}'


def test_status(radiosyno_analysis_info):

    analysis = RadiosynoAnalysis(
        **radiosyno_analysis_info,
        images=ContentFile(b'CT e SPET files', name='images.zip'),
        status='AA',
    )

    with pytest.raises(ValidationError):
        analysis.full_clean()


def test_model_code_and_service_name():

    assert RadiosynoAnalysis.CODE == '04'
    assert RadiosynoAnalysis.SERVICE_NAME_CODE == 'RA'


def test_save_with_conclude_status_must_be_report(clinic_dosimetry):

    with pytest.raises(ValidationError):
        clinic_dosimetry.status = RadiosynoAnalysis.CONCLUDED
        clinic_dosimetry.full_clean()


def test_order_code(radiosyno_analysis):

    clinic_id = radiosyno_analysis.order.user.id
    year = str(radiosyno_analysis.created_at.year)[2:]
    order_id = radiosyno_analysis.order.id
    analysis_id = radiosyno_analysis.id
    isotope = radiosyno_analysis.isotope
    expected = f'{clinic_id:04}.{order_id:04}.{isotope}.{year}/{analysis_id:04}-04'

    assert expected == radiosyno_analysis.code
