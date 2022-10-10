from datetime import datetime

import pytest
from django.contrib.auth import get_user_model
from django.db.utils import IntegrityError

from web_server.service.models import Order


User = get_user_model()


def test_orders_create(clinic_order):
    assert Order.objects.exists()


def test_orders_create_at(clinic_order):
    assert isinstance(clinic_order.created_at, datetime)


def test_orders_modified_at(clinic_order):
    assert isinstance(clinic_order.modified_at, datetime)


def test_delete_user_must_delete_quotes(user, clinic_order):
    user.delete()
    assert not Order.objects.exists()


def test_delete_orders_must_not_delete_user(user, clinic_order):
    clinic_order.delete()
    assert User.objects.exists()


def test_orders_str(clinic_order):
    assert str(clinic_order) == clinic_order.code


def test_orders_positive_integer_constraint(user):
    with pytest.raises(IntegrityError):
        Order.objects.create(user=user, quantity_of_analyzes=-1, remaining_of_analyzes=-1)


def test_orders_one_to_many_relation(user, second_user, tree_orders_of_tow_users):

    assert tree_orders_of_tow_users[0].user.id == user.id
    assert tree_orders_of_tow_users[1].user.id == user.id

    assert tree_orders_of_tow_users[2].user.id == second_user.id

    assert user.orders.count() == 2
    assert second_user.orders.count() == 1


def test_default_values(user):

    order_db = Order.objects.create(
            user=user,
            price='1000', service_name=Order.CLINIC_DOSIMETRY)

    assert not order_db.permission
    assert order_db.quantity_of_analyzes == 0
    assert order_db.remaining_of_analyzes == 0


def test_get_code_service_order(clinic_order):

    assert '01' == clinic_order._code_service()


def test_order_code(clinic_order):

    clinic_id = clinic_order.user.id
    year = str(clinic_order.created_at.year)[2:]
    order_id = clinic_order.id
    expected = f'{clinic_id:04}.{year}/{order_id:04}-01'

    assert expected == clinic_order.code
