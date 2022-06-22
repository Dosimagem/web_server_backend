from decimal import Decimal
import pytest

from web_server.service.models import Info, Order, Service


@pytest.fixture
def user(django_user_model):
    email, password = 'test@email.com', '1234'  # TODO: Extrair isso para uma fixture
    user = django_user_model.objects.create_user(email=email, password=password)
    return user


@pytest.fixture
def service(db):
    return Service.objects.create(name='Dosimetria Clinica',
                                  description='Serviço de dosimentria',
                                  unit_price=Decimal('1855.21'))


@pytest.fixture
def order(user, service):
    return Order.objects.create(requester=user,
                                service=service,
                                amount=2,
                                status=Order.PROCESSING)


@pytest.fixture
def info(order):
    return Info.objects.create(order=order, camera_factor=50.0)
