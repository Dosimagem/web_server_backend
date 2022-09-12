from datetime import datetime

import pytest
from django.contrib.auth import get_user_model
from django.db.utils import IntegrityError

from web_server.service.models import Order


User = get_user_model()


def test_orders_create(user_and_order):
    assert Order.objects.exists()


def test_orders_create_at(user_and_order):
    assert isinstance(user_and_order.created_at, datetime)


def test_orders_modified_at(user_and_order):
    assert isinstance(user_and_order.modified_at, datetime)


def test_delete_user_must_delete_quotes(user, user_and_order):
    user.delete()
    assert not Order.objects.exists()


def test_delete_orders_must_not_delete_user(user, user_and_order):
    user_and_order.delete()
    assert User.objects.exists()


def test_orders_str(user_and_order):
    assert str(user_and_order) == user_and_order.user.profile.name


def test_orders_positive_integer_constraint(user):
    with pytest.raises(IntegrityError):
        Order.objects.create(user=user, quantity_of_analyzes=-1, remaining_of_analyzes=-1)


def test_orders_one_to_many_relation(user, second_user, users_and_orders):

    assert users_and_orders[0].user.id == user.id
    assert users_and_orders[1].user.id == user.id

    assert users_and_orders[2].user.id == second_user.id

    assert user.orders.count() == 2
    assert second_user.orders.count() == 1


def test_default_values(user):

    order_db = Order.objects.create(
            user=user,
            price='1000', service_name=Order.DOSIMETRY_CLINIC)

    assert not order_db.permission
    assert order_db.quantity_of_analyzes == 0
    assert order_db.remaining_of_analyzes == 0


# def test_remaining_of_analyzes_must_be_lower_that_quantity_of_analyzes(user_and_order):

#     order_db = Order.objects.first()

#     order_db.remaining_of_analyzes = order_db.quantity_of_analyzes + 1

#     with pytest.raises(ValidationError):
#         order_db.save()

#     order_db = Order.objects.first()

#     assert order_db.remaining_of_analyzes <= order_db.quantity_of_analyzes
