from decimal import Decimal

import pytest
from web_server.core.models import UserProfile
from rest_framework.authtoken.models import Token

from web_server.service.models import UserQuota


@pytest.fixture
def register_infos():
    return dict(
        email='test1@email.com',
        confirmed_email='test1@email.com',
        password1='123456!!',
        password2='123456!!',
        name='João Silva',
        phone='1111111',
        institution='UFRJ',
        role='Medico'
    )


@pytest.fixture
def user_info():
    return {'email': 'test@email.com', 'password': '123456'}


@pytest.fixture
def user_profile_info():
    return {
        'name': 'User Surname',
        'phone': '(11)999111213',
        'institution': 'Institution Asc',
        'role': 'Medico'
    }

@pytest.fixture
def second_user_info():
    return {'email': 'test2@email.com', 'password': '123456##'}


@pytest.fixture
def second_user_profile_info():
    return {
        'name': 'Second User',
        'phone': '(22)999111213',
        'institution': 'Institution Bsc',
        'role': 'Fisico'
    }



@pytest.fixture
def user(django_user_model, user_info, user_profile_info):
    user = django_user_model.objects.create_user(**user_info)
    UserProfile.objects.filter(user=user).update(**user_profile_info)
    Token.objects.create(user=user)
    return django_user_model.objects.get(id=user.id)


@pytest.fixture
def second_user(user, django_user_model, second_user_info, second_user_profile_info):
    new_user = django_user_model.objects.create_user(**second_user_info)
    UserProfile.objects.filter(user=new_user).update(**second_user_profile_info)
    Token.objects.create(user=new_user)
    return django_user_model.objects.get(id=new_user.id)


@pytest.fixture
def create_quota_data():
    return {
        'amount': 10,
        'price': '1000.00',
        'service_type': UserQuota.DOSIMETRY_CLINIC
    }


@pytest.fixture
def user_quotas(user, create_quota_data):
    return UserQuota.objects.create(user=user,
        amount=create_quota_data['amount'],
        service_type=create_quota_data['service_type'],
        price=create_quota_data['price'],
        status_payment=UserQuota.CONFIRMED,
        )


@pytest.fixture
def logged_user(client, user):
    client.force_login(user)
    return user


# INDEX_DOSIMETRY = 0
# INDEX_DOSIMETRY_PRECLINICAL = 1
# INDEX_SEGMENTANTION = 2
# INDEX_COMPUTATIONAL_MODELING = 3


# @pytest.fixture
# def services(db):

#     Service(name='Dosimetria Clinica',
#             description='Serviço de dosimentria',
#             unit_price=Decimal('1855.21')).save()

#     Service(name='Dosimetria Preclinica',
#             description='Serviço de dosimetria preclinica',
#             unit_price=Decimal('1000.01')).save()

#     Service(name='Segmentação',
#             description='Serviço de Segmentação',
#             unit_price=Decimal('2000.50')).save()

#     Service(name='Modelagem Computacional',
#             description='Serviço de modelagem computacional',
#             unit_price=Decimal('4000.55')).save()

#     return Service.objects.all()


# @pytest.fixture
# def dosimetry_clinical_service(services):
#     return services[INDEX_DOSIMETRY]


# @pytest.fixture
# def dosimetry_preclinical_service(services):
#     return services[INDEX_DOSIMETRY_PRECLINICAL]


# @pytest.fixture
# def segmentantion_service(services):
#     return services[INDEX_SEGMENTANTION]


# @pytest.fixture
# def computational_modeling_service(services):
#     return services[INDEX_COMPUTATIONAL_MODELING]


# DATETIME_TIMEZONE = make_aware(datetime(2016, 12, 14, 11, 2, 51))
# # DATETIME_TIMEZONE = make_aware(utc(2016, 12, 14, 11, 2, 51))


# @pytest.fixture
# def dosimetry_clinical_order(user, dosimetry_clinical_service):

#     return DosimetryOrder.objects.create(requester=user,
#                                          service=dosimetry_clinical_service,
#                                          amount=2,
#                                          status=DosimetryOrder.PROCESSING,
#                                          camera_factor=10.0,
#                                          radionuclide='Lu-177',
#                                          injected_activity=50.0,
#                                          injection_datetime=DATETIME_TIMEZONE,
#                                          images='images.zip'
#                                          )


# @pytest.fixture
# def dosimetry_preclinical_order(user, dosimetry_preclinical_service):

#     return DosimetryOrder.objects.create(requester=user,
#                                          service=dosimetry_preclinical_service,
#                                          amount=2,
#                                          status=DosimetryOrder.PROCESSING,
#                                          camera_factor=10.0,
#                                          radionuclide='L-177',
#                                          injected_activity=50.0,
#                                          injection_datetime=DATETIME_TIMEZONE,
#                                          images='images.zip'
#                                          )


# @pytest.fixture
# def segmentantion_order(user, segmentantion_service):

#     return SegmentationOrder.objects.create(requester=user,
#                                             service=segmentantion_service,
#                                             amount=1,
#                                             status=DosimetryOrder.PROCESSING,
#                                             images='images.zip',
#                                             observations='Texto de observação',
#                                             )


# @pytest.fixture
# def computational_modeling(user, computational_modeling_service):
#     return ComputationalModelOrder.objects.create(requester=user,
#                                                   service=computational_modeling_service,
#                                                   amount=3,
#                                                   status=DosimetryOrder.PROCESSING,
#                                                   images='images.zip',
#                                                   equipment_specification=ComputationalModelOrder.CT,
#                                                   )


# @pytest.fixture
# def orders_user(dosimetry_clinical_order, dosimetry_preclinical_order, segmentantion_order, computational_modeling):
#     return [dosimetry_clinical_order, dosimetry_preclinical_order, segmentantion_order, computational_modeling]
