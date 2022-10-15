from datetime import datetime
from decimal import Decimal

import pytest
from django.core.files.base import ContentFile
from django.utils.timezone import make_aware
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

from web_server.core.models import UserProfile
from web_server.service.models import (
    Calibration,
    ClinicDosimetryAnalysis,
    Isotope,
    Order,
    PreClinicDosimetryAnalysis,
    SegmentationAnalysis,
)

HTTP_METHODS = {
    'get': APIClient().get,
    'post': APIClient().post,
    'put': APIClient().put,
    'patch': APIClient().patch,
    'delete': APIClient().delete,
}


@pytest.fixture(autouse=True)
def disable_SQL_logging(settings):
    settings.LOGGER_SQL = False


@pytest.fixture(autouse=True)
def mediafiles(settings, tmp_path):
    settings.MEDIA_ROOT = tmp_path / 'media'


@pytest.fixture
def client_api():
    return APIClient()


@pytest.fixture
def client_api_auth(client_api, user):
    client_api.credentials(HTTP_AUTHORIZATION='Bearer ' + user.auth_token.key)
    return client_api


@pytest.fixture
def register_infos():
    return dict(
        # User
        email='test1@email.com',
        confirmed_email='test1@email.com',
        password1='123456!!',
        password2='123456!!',
        # Profile
        clinic='Clinica A',
        name='João Silva',
        cnpj='42438610000111',  # 42.438.610/0001-11
        cpf='93743851121',  # 937.438.511-21
        phone='55(33)1111-1111',
        role='Médico',
    )


@pytest.fixture
def user_info(register_infos):
    return dict(email=register_infos['email'], password=register_infos['password1'])


@pytest.fixture
def user_profile_info(register_infos):
    return {
        'name': register_infos['name'],
        'phone': register_infos['phone'],
        'clinic': register_infos['clinic'],
        'role': register_infos['role'],
        'cpf': register_infos['cpf'],
        'cnpj': register_infos['cnpj'],
    }


@pytest.fixture
def second_register_infos():
    return dict(
        # User
        email='test2@email.com',
        confirmed_email='test2@email.com',
        password1='123456!!',
        password2='123456!!',
        # Profile
        clinic='Clinica B',
        name='Maria Silva',
        cnpj='83398534000145',  # 83.398.534/0001-45
        cpf='52450318097',  # 524.503.180-97
        phone='55(41)22222-2222',
        role='Fisica médica',
    )


@pytest.fixture
def second_user_login_info(second_register_infos):
    return dict(
        email=second_register_infos['email'],
        password=second_register_infos['password1'],
    )


@pytest.fixture
def second_user_profile_info(second_register_infos):
    return {
        'name': second_register_infos['name'],
        'phone': second_register_infos['phone'],
        'clinic': second_register_infos['clinic'],
        'role': second_register_infos['role'],
        'cpf': second_register_infos['cpf'],
        'cnpj': second_register_infos['cnpj'],
    }


@pytest.fixture
def user(django_user_model, user_info, user_profile_info):
    user = django_user_model.objects.create_user(**user_info)
    user.email_verified = True
    user.save()
    UserProfile.objects.filter(user=user).update(**user_profile_info)
    Token.objects.create(user=user)
    return django_user_model.objects.get(id=user.id)


@pytest.fixture
def second_user(user, django_user_model, second_user_login_info, second_user_profile_info):
    new_user = django_user_model.objects.create_user(**second_user_login_info)
    UserProfile.objects.filter(user=new_user).update(**second_user_profile_info)
    Token.objects.create(user=new_user)
    return django_user_model.objects.get(id=new_user.id)


@pytest.fixture
def create_order_data(user):
    return {
        'user': user,
        'quantity_of_analyzes': 10,
        'remaining_of_analyzes': 10,
        'price': '1000.00',
        'service_name': Order.CLINIC_DOSIMETRY,
        'status_payment': Order.AWAITING_PAYMENT,
    }


@pytest.fixture
def clinic_order(user, create_order_data):
    return Order.objects.create(
        user=user,
        quantity_of_analyzes=create_order_data['quantity_of_analyzes'],
        remaining_of_analyzes=create_order_data['remaining_of_analyzes'],
        price=create_order_data['price'],
        service_name=create_order_data['service_name'],
    )


@pytest.fixture
def preclinic_order(user):
    return Order.objects.create(
        user=user,
        quantity_of_analyzes=10,
        remaining_of_analyzes=10,
        price='1000',
        service_name=Order.PRECLINIC_DOSIMETRY,
    )


@pytest.fixture
def segmentation_order(user):
    return Order.objects.create(
        user=user,
        quantity_of_analyzes=10,
        remaining_of_analyzes=10,
        price='1000',
        service_name=Order.SEGMENTANTION_QUANTIFICATION,
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
        service_name=Order.CLINIC_DOSIMETRY,
        status_payment=Order.CONFIRMED,
        permission=True,
    )

    Order.objects.create(
        user=user,
        quantity_of_analyzes=5,
        remaining_of_analyzes=5,
        price=Decimal('5000.00'),
        service_name=Order.PRECLINIC_DOSIMETRY,
        status_payment=Order.AWAITING_PAYMENT,
        permission=False,
    )

    Order.objects.create(
        user=second_user,
        quantity_of_analyzes=3,
        remaining_of_analyzes=3,
        price=Decimal('3000.00'),
        service_name=Order.CLINIC_DOSIMETRY,
        status_payment=Order.AWAITING_PAYMENT,
        permission=False,
    )

    return list(Order.objects.all())


@pytest.fixture
def lu_177(db):
    return Isotope.objects.create(name='Lu-177')


@pytest.fixture
def lu_177_and_cu_64(lu_177):
    Isotope.objects.create(name='Cu-64')
    return list(Isotope.objects.all())


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
def api_cnpj_successfull(responses, register_infos):
    return responses.add(
        method='GET',
        url=f'https://brasilapi.com.br/api/cnpj/v1/{register_infos["cnpj"]}',
        status=200,
    )


@pytest.fixture
def api_cnpj_fail(responses, second_register_infos):
    return responses.add(
        method='GET',
        url=f'https://brasilapi.com.br/api/cnpj/v1/{second_register_infos["cnpj"]}',
        status=404,
        json={'message': ['CNPJ 83.398.534/0001-45 não encontrado.']},
    )


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
def clinic_dosimetry(clinic_dosimetry_info, clinic_dosimetry_file):

    # TODO: Pensar em uma solução melhor, talvez usar um serviço para isso
    order_uuid = clinic_dosimetry_info['order'].uuid
    order = Order.objects.get(uuid=order_uuid)
    order.remaining_of_analyzes -= 1
    order.save()

    analysis = ClinicDosimetryAnalysis.objects.create(**clinic_dosimetry_info, **clinic_dosimetry_file)
    return analysis


@pytest.fixture
def clinic_dosi_update_or_del_is_possible(clinic_dosimetry):
    clinic_dosimetry.status = ClinicDosimetryAnalysis.INVALID_INFOS
    clinic_dosimetry.save()
    return clinic_dosimetry


@pytest.fixture
def preclinic_dosimetry(preclinic_dosimetry_info, preclinic_dosimetry_file):

    # TODO: Pensar em uma solução melhor, talvez usar um serviço para isso
    order_uuid = preclinic_dosimetry_info['order'].uuid
    order = Order.objects.get(uuid=order_uuid)
    order.remaining_of_analyzes -= 1
    order.save()

    analysis = PreClinicDosimetryAnalysis.objects.create(**preclinic_dosimetry_info, **preclinic_dosimetry_file)

    return analysis


@pytest.fixture
def preclinic_dosi_update_del_is_possible(preclinic_dosimetry):
    preclinic_dosimetry.status = PreClinicDosimetryAnalysis.INVALID_INFOS
    preclinic_dosimetry.save()
    return preclinic_dosimetry


@pytest.fixture
def segmentation_analysis(segmentation_analysis_info, segmentation_analysis_file):

    # TODO: Pensar em uma solução melhor, talvez usar um serviço para isso
    order_uuid = segmentation_analysis_info['order'].uuid
    order = Order.objects.get(uuid=order_uuid)
    order.remaining_of_analyzes -= 1
    order.save()

    analysis = SegmentationAnalysis.objects.create(**segmentation_analysis_info, **segmentation_analysis_file)

    return analysis


@pytest.fixture
def seg_analysis_update_or_del_is_possible(segmentation_analysis):
    segmentation_analysis.status = SegmentationAnalysis.INVALID_INFOS
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
