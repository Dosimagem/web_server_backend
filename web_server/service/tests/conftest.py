from datetime import datetime
from decimal import Decimal

import pytest
from django.core.files.base import ContentFile
from django.utils.timezone import make_aware

from web_server.service.models import (
    Calibration,
    ClinicDosimetryAnalysis,
    Isotope,
    IsotopeRadiosyno,
    Order,
    PreClinicDosimetryAnalysis,
    RadiosynoAnalysis,
    SegmentationAnalysis,
)


@pytest.fixture
def form_data(calibration_infos, calibration_file):  # TODO change name for first_http_data_calibration

    return {
        'isotope': calibration_infos['isotope'].name,
        'calibrationName': calibration_infos['calibration_name'],
        'syringeActivity': calibration_infos['syringe_activity'],
        'residualSyringeActivity': calibration_infos['residual_syringe_activity'],
        'measurementDatetime': calibration_infos['measurement_datetime'],
        'phantomVolume': calibration_infos['phantom_volume'],
        'acquisitionTime': calibration_infos['acquisition_time'],
        'images': calibration_file['images'],
    }


@pytest.fixture
def second_form_data(second_calibration_infos, calibration_file):  # TODO change name for second_http_data_calibration
    return {
        'isotope': second_calibration_infos['isotope'].name,
        'calibrationName': second_calibration_infos['calibration_name'],
        'syringeActivity': second_calibration_infos['syringe_activity'],
        'residualSyringeActivity': second_calibration_infos['residual_syringe_activity'],
        'measurementDatetime': second_calibration_infos['measurement_datetime'],
        'phantomVolume': second_calibration_infos['phantom_volume'],
        'acquisitionTime': second_calibration_infos['acquisition_time'],
        'images': calibration_file['images'],
    }


@pytest.fixture
def form_data_clinic_dosimetry(clinic_dosimetry_info, clinic_dosimetry_file):

    return {
        'calibrationId': clinic_dosimetry_info['calibration'].uuid,
        'images': clinic_dosimetry_file['images'],
        'analysisName': clinic_dosimetry_info['analysis_name'],
        'injectedActivity': clinic_dosimetry_info['injected_activity'],
        'administrationDatetime': clinic_dosimetry_info['administration_datetime'],
    }


@pytest.fixture
def form_data_preclinic_dosimetry(preclinic_dosimetry_info, preclinic_dosimetry_file):

    return {
        'calibrationId': preclinic_dosimetry_info['calibration'].uuid,
        'images': preclinic_dosimetry_file['images'],
        'analysisName': preclinic_dosimetry_info['analysis_name'],
        'injectedActivity': preclinic_dosimetry_info['injected_activity'],
        'administrationDatetime': preclinic_dosimetry_info['administration_datetime'],
    }


@pytest.fixture
def form_data_segmentation_analysis(segmentation_analysis_info, segmentation_analysis_file):

    return {
        'images': segmentation_analysis_file['images'],
        'analysisName': segmentation_analysis_info['analysis_name'],
    }


@pytest.fixture
def form_data_radiosyno_analysis(radiosyno_analysis_info, radiosyno_analysis_file, y_90):

    return {
        'images': radiosyno_analysis_file['images'],
        'analysisName': radiosyno_analysis_info['analysis_name'],
        'isotope': y_90,
    }


@pytest.fixture
def create_order_data(user):
    return {
        'user': user,
        'quantity_of_analyzes': 10,
        'remaining_of_analyzes': 10,
        'price': '1000.00',
        'service_name': Order.ServicesName.CLINIC_DOSIMETRY.value,
        'status_payment': Order.PaymentStatus.CONFIRMED,
    }


@pytest.fixture
def clinic_order(user, create_order_data):
    return Order.objects.create(
        user=user,
        quantity_of_analyzes=create_order_data['quantity_of_analyzes'],
        remaining_of_analyzes=create_order_data['remaining_of_analyzes'],
        price=create_order_data['price'],
        service_name=create_order_data['service_name'],
        status_payment=Order.PaymentStatus.CONFIRMED,
    )


@pytest.fixture
def preclinic_order(user):
    return Order.objects.create(
        user=user,
        quantity_of_analyzes=10,
        remaining_of_analyzes=10,
        price='1000',
        service_name=Order.ServicesName.PRECLINIC_DOSIMETRY.value,
        status_payment=Order.PaymentStatus.CONFIRMED,
    )


@pytest.fixture
def segmentation_order(user):
    return Order.objects.create(
        user=user,
        quantity_of_analyzes=10,
        remaining_of_analyzes=10,
        price='1000',
        service_name=Order.ServicesName.SEGMENTANTION_QUANTIFICATION.value,
        status_payment=Order.PaymentStatus.CONFIRMED,
    )


@pytest.fixture
def radiosyno_order(user):
    return Order.objects.create(
        user=user,
        quantity_of_analyzes=10,
        remaining_of_analyzes=10,
        price='1000',
        service_name=Order.ServicesName.RADIOSYNOVIORTHESIS.value,
        status_payment=Order.PaymentStatus.CONFIRMED,
    )


@pytest.fixture
def tree_orders_of_two_diff_users(user, second_user):
    """
    Order Table:

    ID_USER  Type               Number    Value   Status Payment
    1        Dosimetry Clinic     10     10.000   Confirmed
    1        Dosimetry Preclinic   5      5.000   Analysis
    2        Dosimetry Clinic      3      3.000   Confimed
    """

    Order.objects.create(
        user=user,
        quantity_of_analyzes=10,
        remaining_of_analyzes=10,
        price=Decimal('10000.00'),
        service_name=Order.ServicesName.CLINIC_DOSIMETRY.value,
        status_payment=Order.PaymentStatus.CONFIRMED,
        active=True,
    )

    Order.objects.create(
        user=user,
        quantity_of_analyzes=5,
        remaining_of_analyzes=5,
        price=Decimal('5000.00'),
        service_name=Order.ServicesName.PRECLINIC_DOSIMETRY.value,
        status_payment=Order.PaymentStatus.AWAITING_PAYMENT,
        active=False,
    )

    Order.objects.create(
        user=second_user,
        quantity_of_analyzes=3,
        remaining_of_analyzes=3,
        price=Decimal('3000.00'),
        service_name=Order.ServicesName.CLINIC_DOSIMETRY.value,
        status_payment=Order.PaymentStatus.AWAITING_PAYMENT,
        active=False,
    )

    return list(Order.objects.all())


@pytest.fixture
def lu_177(db):
    return Isotope.objects.create(name='Lu-177')


@pytest.fixture
def lu_177_and_cu_64(lu_177):
    Isotope.objects.create(name='Cu-64')
    return list(Isotope.objects.all())


@pytest.fixture
def y_90(db):
    return IsotopeRadiosyno.objects.create(name='Y-90')


DATETIME_TIMEZONE = make_aware(datetime(2016, 12, 14, 11, 2, 51))


@pytest.fixture
def calibration_file():
    fp = ContentFile(b'file_content', name='images.zip')
    return {'images': fp}


@pytest.fixture
def calibration_infos(user, lu_177):
    return dict(
        user=user,
        isotope=lu_177,
        calibration_name='Calibration 1',
        syringe_activity=50.0,
        residual_syringe_activity=0.3,
        measurement_datetime=DATETIME_TIMEZONE,
        phantom_volume=200.0,
        acquisition_time=1800.0,
    )


@pytest.fixture
def second_calibration_infos(user, lu_177):
    return dict(
        user=user,
        isotope=lu_177,
        calibration_name='Calibration 2',
        syringe_activity=50.0,
        residual_syringe_activity=0.3,
        measurement_datetime=DATETIME_TIMEZONE,
        phantom_volume=200.0,
        acquisition_time=1000.0,
    )


@pytest.fixture
def first_calibration(calibration_infos):
    return Calibration.objects.create(**calibration_infos)


@pytest.fixture
def second_calibration(first_calibration, second_calibration_infos):
    return Calibration.objects.create(**second_calibration_infos)


@pytest.fixture
def calibration_with_images(calibration_infos, calibration_file):
    return Calibration.objects.create(**calibration_infos, **calibration_file)


@pytest.fixture
def second_user_calibrations_infos(second_user, lu_177_and_cu_64):

    c1 = dict(
        user=second_user,
        isotope=lu_177_and_cu_64[0],
        calibration_name='Calibration A',
        syringe_activity=500.0,
        residual_syringe_activity=2.3,
        measurement_datetime=DATETIME_TIMEZONE,
        phantom_volume=20.0,
        acquisition_time=10000.0,
    )

    c2 = dict(
        user=second_user,
        isotope=lu_177_and_cu_64[1],
        calibration_name='Calibration B',
        syringe_activity=25.0,
        residual_syringe_activity=10.3,
        measurement_datetime=DATETIME_TIMEZONE,
        phantom_volume=500.0,
        acquisition_time=1800.0,
    )

    return [c1, c2]


@pytest.fixture
def second_user_calibrations(second_user_calibrations_infos, second_user):
    Calibration.objects.create(**second_user_calibrations_infos[0])
    Calibration.objects.create(**second_user_calibrations_infos[1])

    return list(Calibration.objects.filter(user=second_user))


@pytest.fixture
def clinic_dosimetry_file():
    fp = ContentFile(b'CT e SPET files', name='images.zip')
    return {'images': fp}


@pytest.fixture
def preclinic_dosimetry_file():
    fp = ContentFile(b'CT e SPET files', name='images.zip')
    return {'images': fp}


@pytest.fixture
def segmentation_analysis_file():
    fp = ContentFile(b'CT files', name='images.zip')
    return {'images': fp}


@pytest.fixture
def radiosyno_analysis_file():
    fp = ContentFile(b'CT e SPET files', name='images.zip')
    return {'images': fp}


@pytest.fixture
def clinic_dosimetry_info(first_calibration, clinic_order):
    return {
        'calibration': first_calibration,
        'order': clinic_order,
        'analysis_name': 'Analysis 1',
        'injected_activity': 50,
        'administration_datetime': DATETIME_TIMEZONE,
    }


@pytest.fixture
def preclinic_dosimetry_info(first_calibration, preclinic_order):
    return {
        'calibration': first_calibration,
        'order': preclinic_order,
        'analysis_name': 'Analysis 1',
        'injected_activity': 20,
        'administration_datetime': DATETIME_TIMEZONE,
    }


@pytest.fixture
def segmentation_analysis_info(segmentation_order):
    return {
        'order': segmentation_order,
        'analysis_name': 'Analysis 1',
    }


@pytest.fixture
def radiosyno_analysis_info(radiosyno_order, y_90):
    return {'order': radiosyno_order, 'analysis_name': 'Analysis 1', 'isotope': y_90}


@pytest.fixture
def clinic_dosimetry(clinic_dosimetry_info, clinic_dosimetry_file):

    # TODO: Pensar em uma solução melhor, talvez usar um serviço para isso
    order_uuid = clinic_dosimetry_info['order'].uuid
    order = Order.objects.get(uuid=order_uuid)
    order.remaining_of_analyzes -= 1
    order.save()

    analysis = ClinicDosimetryAnalysis.objects.create(
        **clinic_dosimetry_info, **clinic_dosimetry_file, status=ClinicDosimetryAnalysis.Status.ANALYZING_INFOS
    )
    return analysis


@pytest.fixture
def clinic_dosi_update_or_del_is_possible(clinic_dosimetry):
    clinic_dosimetry.status = ClinicDosimetryAnalysis.Status.INVALID_INFOS
    clinic_dosimetry.save()
    return clinic_dosimetry


@pytest.fixture
def preclinic_dosimetry(preclinic_dosimetry_info, preclinic_dosimetry_file):

    # TODO: Pensar em uma solução melhor, talvez usar um serviço para isso
    order_uuid = preclinic_dosimetry_info['order'].uuid
    order = Order.objects.get(uuid=order_uuid)
    order.remaining_of_analyzes -= 1
    order.save()

    analysis = PreClinicDosimetryAnalysis.objects.create(
        **preclinic_dosimetry_info, **preclinic_dosimetry_file, status=ClinicDosimetryAnalysis.Status.ANALYZING_INFOS
    )

    return analysis


@pytest.fixture
def preclinic_dosi_update_del_is_possible(preclinic_dosimetry):
    preclinic_dosimetry.status = PreClinicDosimetryAnalysis.Status.DATA_SENT
    preclinic_dosimetry.save()
    return preclinic_dosimetry


@pytest.fixture
def radiosyno_analysis(radiosyno_analysis_info, radiosyno_analysis_file):

    # TODO: Pensar em uma solução melhor, talvez usar um serviço para isso
    order_uuid = radiosyno_analysis_info['order'].uuid
    order = Order.objects.get(uuid=order_uuid)
    order.remaining_of_analyzes -= 1
    order.save()

    analysis = RadiosynoAnalysis.objects.create(
        **radiosyno_analysis_info, **radiosyno_analysis_file, status=RadiosynoAnalysis.Status.ANALYZING_INFOS
    )
    return analysis


@pytest.fixture
def radiosyno_analysis_update_or_del_is_possible(radiosyno_analysis):
    radiosyno_analysis.status = RadiosynoAnalysis.Status.INVALID_INFOS
    radiosyno_analysis.save()
    return radiosyno_analysis


@pytest.fixture
def segmentation_analysis(segmentation_analysis_info, segmentation_analysis_file):

    # TODO: Pensar em uma solução melhor, talvez usar um serviço para isso
    order_uuid = segmentation_analysis_info['order'].uuid
    order = Order.objects.get(uuid=order_uuid)
    order.remaining_of_analyzes -= 1
    order.save()

    analysis = SegmentationAnalysis.objects.create(
        **segmentation_analysis_info,
        **segmentation_analysis_file,
        status=ClinicDosimetryAnalysis.Status.ANALYZING_INFOS,
    )

    return analysis


@pytest.fixture
def seg_analysis_update_or_del_is_possible(segmentation_analysis):
    segmentation_analysis.status = SegmentationAnalysis.Status.INVALID_INFOS
    segmentation_analysis.save()
    return segmentation_analysis


@pytest.fixture
def tree_clinic_dosimetry_of_first_user(clinic_dosimetry_info):

    clinic_dosimetry_info['analysis_name'] = 'Analysis 1'
    ClinicDosimetryAnalysis.objects.create(
        **clinic_dosimetry_info,
        images=ContentFile(b'CT e SPET files 1', name='images.zip'),
    )

    clinic_dosimetry_info['analysis_name'] = 'Analysis 2'
    ClinicDosimetryAnalysis.objects.create(
        **clinic_dosimetry_info,
        images=ContentFile(b'CT e SPET files 2', name='images.zip'),
    )

    clinic_dosimetry_info['analysis_name'] = 'Analysis 3'
    ClinicDosimetryAnalysis.objects.create(
        **clinic_dosimetry_info,
        images=ContentFile(b'CT e SPET files 3', name='images.zip'),
    )
    return ClinicDosimetryAnalysis.objects.all()


@pytest.fixture
def tree_preclinic_dosimetry_of_first_user(preclinic_dosimetry_info):

    preclinic_dosimetry_info['analysis_name'] = 'Analysis 1'
    PreClinicDosimetryAnalysis.objects.create(
        **preclinic_dosimetry_info,
        images=ContentFile(b'CT e SPET files 1', name='images.zip'),
    )

    preclinic_dosimetry_info['analysis_name'] = 'Analysis 2'
    PreClinicDosimetryAnalysis.objects.create(
        **preclinic_dosimetry_info,
        images=ContentFile(b'CT e SPET files 2', name='images.zip'),
    )

    preclinic_dosimetry_info['analysis_name'] = 'Analysis 3'
    PreClinicDosimetryAnalysis.objects.create(
        **preclinic_dosimetry_info,
        images=ContentFile(b'CT e SPET files 3', name='images.zip'),
    )
    return PreClinicDosimetryAnalysis.objects.all()


@pytest.fixture
def tree_segmentation_analysis_of_first_user(segmentation_analysis_info):

    segmentation_analysis_info['analysis_name'] = 'Analysis 1'
    SegmentationAnalysis.objects.create(
        **segmentation_analysis_info,
        images=ContentFile(b'CT files 1', name='images.zip'),
    )

    segmentation_analysis_info['analysis_name'] = 'Analysis 2'
    SegmentationAnalysis.objects.create(
        **segmentation_analysis_info,
        images=ContentFile(b'CT files 2', name='images.zip'),
    )

    segmentation_analysis_info['analysis_name'] = 'Analysis 3'
    SegmentationAnalysis.objects.create(
        **segmentation_analysis_info,
        images=ContentFile(b'CT files 3', name='images.zip'),
    )
    return SegmentationAnalysis.objects.all()


@pytest.fixture
def tree_radiosyno_analysis_of_first_user(radiosyno_analysis_info):

    radiosyno_analysis_info['analysis_name'] = 'Analysis 1'
    RadiosynoAnalysis.objects.create(
        **radiosyno_analysis_info,
        images=ContentFile(b'CT files 1', name='images.zip'),
    )

    radiosyno_analysis_info['analysis_name'] = 'Analysis 2'
    RadiosynoAnalysis.objects.create(
        **radiosyno_analysis_info,
        images=ContentFile(b'CT files 2', name='images.zip'),
    )

    radiosyno_analysis_info['analysis_name'] = 'Analysis 3'
    RadiosynoAnalysis.objects.create(
        **radiosyno_analysis_info,
        images=ContentFile(b'CT files 3', name='images.zip'),
    )

    return RadiosynoAnalysis.objects.all()
