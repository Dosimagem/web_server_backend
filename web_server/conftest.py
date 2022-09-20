from datetime import datetime
from decimal import Decimal

import pytest
from django.core.files.base import ContentFile
from rest_framework.authtoken.models import Token
from django.utils.timezone import make_aware

from web_server.core.models import UserProfile
from web_server.service.models import ClinicDosimetryAnalysis, Isotope, Order, Calibration, PreClinicDosimetryAnalysis


@pytest.fixture(autouse=True)
def mediafiles(settings, tmp_path):
    settings.MEDIA_ROOT = tmp_path / 'media'


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
        phone='11111111',
        role='Médico'
    )


@pytest.fixture
def user_info(register_infos):
    return dict(
        email=register_infos['email'],
        password=register_infos['password1']
    )


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
        phone='22222222',
        role='Fisica médica'
    )


@pytest.fixture
def second_user_login_info(second_register_infos):
    return dict(
        email=second_register_infos['email'],
        password=second_register_infos['password1']
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
        'status_payment': Order.AWAITING_PAYMENT
    }


@pytest.fixture
def order(user, create_order_data):  # TODO: change name for clinic order
    return Order.objects.create(user=user,
                                quantity_of_analyzes=create_order_data['quantity_of_analyzes'],
                                remaining_of_analyzes=create_order_data['remaining_of_analyzes'],
                                price=create_order_data['price'],
                                service_name=create_order_data['service_name']
                                )


@pytest.fixture
def preclinic_order(user, create_order_data):
    return Order.objects.create(user=user,
                                quantity_of_analyzes=10,
                                remaining_of_analyzes=10,
                                price='1000',
                                service_name=Order.PRECLINIC_DOSIMETRY
                                )


@pytest.fixture
def tree_orders_of_tow_users(user, second_user):  # TODO: change this to tree_orders_of_tow_users
    '''
    Order Table:

    ID_USER  Type               Number    Value   Status Payment
    1        Dosimetry Clinic     10     10.000   Confirmed
    1        Dosimetry Preclinic   5      5.000   Analysis
    2        Dosimetry Clinic      3      3.000   Confimed
    '''

    Order.objects.create(user=user,
                         quantity_of_analyzes=10,
                         remaining_of_analyzes=10,
                         price=Decimal('10000.00'),
                         service_name=Order.CLINIC_DOSIMETRY,
                         status_payment=Order.CONFIRMED,
                         permission=True
                         )

    Order.objects.create(user=user,
                         quantity_of_analyzes=5,
                         remaining_of_analyzes=5,
                         price=Decimal('5000.00'),
                         service_name=Order.PRECLINIC_DOSIMETRY,
                         status_payment=Order.ANALYSIS,
                         permission=False
                         )

    Order.objects.create(user=second_user,
                         quantity_of_analyzes=3,
                         remaining_of_analyzes=3,
                         price=Decimal('3000.00'),
                         service_name=Order.CLINIC_DOSIMETRY,
                         status_payment=Order.AWAITING_PAYMENT,
                         permission=False
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
        acquisition_time=1000.0
    )


@pytest.fixture
def calibration(calibration_infos):
    return Calibration.objects.create(**calibration_infos)


@pytest.fixture
def second_calibration(calibration, second_calibration_infos):
    return Calibration.objects.create(**second_calibration_infos)


@pytest.fixture
def calibration_with_images(calibration_infos, calibration_file):
    return Calibration.objects.create(**calibration_infos, **calibration_file)


@pytest.fixture
def firsts_user_calibrations(second_calibration, user):
    return list(Calibration.objects.filter(user=user))


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
            acquisition_time=10000.0
        )

    c2 = dict(
            user=second_user,
            isotope=lu_177_and_cu_64[1],
            calibration_name='Calibration B',
            syringe_activity=25.0,
            residual_syringe_activity=10.3,
            measurement_datetime=DATETIME_TIMEZONE,
            phantom_volume=500.0,
            acquisition_time=1800.0
        )

    return [c1, c2]


@pytest.fixture
def second_user_calibrations(second_user_calibrations_infos, second_user):
    Calibration.objects.create(**second_user_calibrations_infos[0])
    Calibration.objects.create(**second_user_calibrations_infos[1])

    return list(Calibration.objects.filter(user=second_user))


@pytest.fixture
def form_data(calibration_infos, calibration_file):

    return {
         'isotope': calibration_infos['isotope'].name,
         'calibrationName': calibration_infos['calibration_name'],
         'syringeActivity': calibration_infos['syringe_activity'],
         'residualSyringeActivity': calibration_infos['residual_syringe_activity'],
         'measurementDatetime': calibration_infos['measurement_datetime'],
         'phantomVolume': calibration_infos['phantom_volume'],
         'acquisitionTime': calibration_infos['acquisition_time'],
         'images': calibration_file['images']
    }


@pytest.fixture
def second_form_data(second_calibration_infos, calibration_file):
    return {
         'isotope': second_calibration_infos['isotope'].name,
         'calibrationName': second_calibration_infos['calibration_name'],
         'syringeActivity': second_calibration_infos['syringe_activity'],
         'residualSyringeActivity': second_calibration_infos['residual_syringe_activity'],
         'measurementDatetime': second_calibration_infos['measurement_datetime'],
         'phantomVolume': second_calibration_infos['phantom_volume'],
         'acquisitionTime': second_calibration_infos['acquisition_time'],
         'images': calibration_file['images']
    }


@pytest.fixture
def api_cnpj_successfull(responses, register_infos):
    return responses.add(
        method='GET',
        url=f'https://brasilapi.com.br/api/cnpj/v1/{register_infos["cnpj"]}',
        status=200
    )


@pytest.fixture
def api_cnpj_fail(responses, second_register_infos):
    return responses.add(
        method='GET',
        url=f'https://brasilapi.com.br/api/cnpj/v1/{second_register_infos["cnpj"]}',
        status=404,
        json={'message': ['CNPJ 83.398.534/0001-45 não encontrado.']}
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
def clinic_dosimetry_info(user, calibration, order):
    return {
        'user': user,
        'calibration': calibration,
        'order': order,
    }


@pytest.fixture
def preclinic_dosimetry_info(user, calibration, preclinic_order):
    return {
        'user': user,
        'calibration': calibration,
        'order': preclinic_order,
    }


@pytest.fixture
def clinic_dosimetry(clinic_dosimetry_info, clinic_dosimetry_file):
    return ClinicDosimetryAnalysis.objects.create(**clinic_dosimetry_info, **clinic_dosimetry_file)


@pytest.fixture
def preclinic_dosimetry(preclinic_dosimetry_info, preclinic_dosimetry_file):
    return ClinicDosimetryAnalysis.objects.create(**preclinic_dosimetry_info, **preclinic_dosimetry_file)


@pytest.fixture
def tree_clinic_dosimetry_of_first_user(clinic_dosimetry_info):
    ClinicDosimetryAnalysis.objects.create(**clinic_dosimetry_info,
                                           images=ContentFile(b'CT e SPET files 1', name='images.zip'))
    ClinicDosimetryAnalysis.objects.create(**clinic_dosimetry_info,
                                           images=ContentFile(b'CT e SPET files 2', name='images.zip'))
    ClinicDosimetryAnalysis.objects.create(**clinic_dosimetry_info,
                                           images=ContentFile(b'CT e SPET files 3', name='images.zip'))
    return ClinicDosimetryAnalysis.objects.all()


@pytest.fixture
def tree_preclinic_dosimetry_of_first_user(preclinic_dosimetry_info):
    PreClinicDosimetryAnalysis.objects.create(**preclinic_dosimetry_info,
                                              images=ContentFile(b'CT e SPET files 1', name='images.zip'))
    PreClinicDosimetryAnalysis.objects.create(**preclinic_dosimetry_info,
                                              images=ContentFile(b'CT e SPET files 2', name='images.zip'))
    PreClinicDosimetryAnalysis.objects.create(**preclinic_dosimetry_info,
                                              images=ContentFile(b'CT e SPET files 3', name='images.zip'))
    return PreClinicDosimetryAnalysis.objects.all()
