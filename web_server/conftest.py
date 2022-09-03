from decimal import Decimal

import pytest
from web_server.core.models import UserProfile
from rest_framework.authtoken.models import Token

from web_server.service.models import Isotope, Order


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
def create_order_data(user):
    return {
        'user': user,
        'quantity_of_analyzes': 10,
        'remaining_of_analyzes': 10,
        'price': '1000.00',
        'service_name': Order.DOSIMETRY_CLINIC,
        'status_payment': Order.AWAITING_PAYMENT
    }


@pytest.fixture
def user_and_order(user, create_order_data):  # TODO: change this to order
    return Order.objects.create(user=user,
                                quantity_of_analyzes=create_order_data['quantity_of_analyzes'],
                                remaining_of_analyzes=create_order_data['remaining_of_analyzes'],
                                price=create_order_data['price'],
                                service_name=create_order_data['service_name']
                                )


@pytest.fixture
def users_and_orders(user, second_user):  # TODO: change this to tree_orders_of_tow_ursers
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
                         service_name=Order.DOSIMETRY_CLINIC,
                         status_payment=Order.CONFIRMED,
                         permission=True
                         )

    Order.objects.create(user=user,
                         quantity_of_analyzes=5,
                         remaining_of_analyzes=5,
                         price=Decimal('5000.00'),
                         service_name=Order.DOSIMETRY_PRECLINIC,
                         status_payment=Order.ANALYSIS,
                         permission=False
                         )

    Order.objects.create(user=second_user,
                         quantity_of_analyzes=3,
                         remaining_of_analyzes=3,
                         price=Decimal('3000.00'),
                         service_name=Order.DOSIMETRY_CLINIC,
                         status_payment=Order.AWAITING_PAYMENT,
                         permission=False
                         )

    return list(Order.objects.all())


@pytest.fixture
def lu_177(db):
    return Isotope.objects.create(name='Lu-177')


# INDEX_DOSIMETRY = 0
# INDEX_DOSIMETRY_PRECLINICAL = 1
# INDEX_SEGMENTANTION = 2
# INDEX_COMPUTATIONAL_MODELING = 3


# @pytest.fixture
# def Orders(db):

#     Order(name='Dosimetria Clinica',
#             description='Serviço de dosimentria',
#             unit_price=Decimal('1855.21')).save()

#     Order(name='Dosimetria Preclinica',
#             description='Serviço de dosimetria preclinica',
#             unit_price=Decimal('1000.01')).save()

#     Order(name='Segmentação',
#             description='Serviço de Segmentação',
#             unit_price=Decimal('2000.50')).save()

#     Order(name='Modelagem Computacional',
#             description='Serviço de modelagem computacional',
#             unit_price=Decimal('4000.55')).save()

#     return Order.objects.all()


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
