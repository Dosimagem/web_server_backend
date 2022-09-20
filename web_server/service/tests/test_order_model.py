from datetime import datetime

import pytest
from django.contrib.auth import get_user_model
from django.db.utils import IntegrityError

from web_server.service.models import Order


User = get_user_model()


def test_orders_create(order):
    assert Order.objects.exists()


def test_orders_create_at(order):
    assert isinstance(order.created_at, datetime)


def test_orders_modified_at(order):
    assert isinstance(order.modified_at, datetime)


def test_delete_user_must_delete_quotes(user, order):
    user.delete()
    assert not Order.objects.exists()


def test_delete_orders_must_not_delete_user(user, order):
    order.delete()
    assert User.objects.exists()


def test_orders_str(order):
    assert str(order) == f'{order.user.profile.clinic} <{order.get_service_name_display()}>'


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


# def test_remaining_of_analyzes_must_be_lower_that_quantity_of_analyzes(order):

#     order_db = Order.objects.first()

#     order_db.remaining_of_analyzes = order_db.quantity_of_analyzes + 1

#     with pytest.raises(ValidationError):
#         order_db.save()

#     order_db = Order.objects.first()

#     assert order_db.remaining_of_analyzes <= order_db.quantity_of_analyzes
