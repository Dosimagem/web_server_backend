from datetime import datetime

from django.contrib.auth import get_user_model

from web_server.notification.models import Notification

User = get_user_model()


def test_notification_create(notification):
    assert Notification.objects.exists()


def test_create_at(notification):
    assert isinstance(notification.created_at, datetime)


def test_modified_at(notification):
    assert isinstance(notification.modified_at, datetime)


def test_delete_user_must_delete_notification(user, notification):
    user.delete()
    assert not Notification.objects.exists()


def test_delete_notification_must_not_delete_user(user, notification):
    notification.delete()
    assert User.objects.exists()


def test_str(notification):
    assert notification.message == str(notification)


def test_default_values(user):

    notification = Notification.objects.create(user=user, message='Teste', kind=Notification.Kind.SUCCESS)

    assert not notification.checked


def test_toogle(user):
    notification = Notification.objects.create(user=user, message='Teste', kind=Notification.Kind.SUCCESS)

    assert not notification.checked

    notification.toogle()

    assert notification.checked


def test_one_to_many_relation(user, list_notifications):

    assert list_notifications[0].user.id == user.id

    assert len(list_notifications) == user.notifications.count()
