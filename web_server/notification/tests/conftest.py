import pytest

from web_server.notification.models import Notification


@pytest.fixture
def notification(user, faker):
    return Notification.objects.create(user=user, message=faker.sentence(nb_words=10), kind=Notification.Kind.SUCCESS)


@pytest.fixture
def list_notifications(user, faker):
    list_ = [
        Notification(user=user, checked=True, message=faker.sentence(nb_words=10), kind=Notification.Kind.SUCCESS),
        Notification(user=user, message=faker.sentence(nb_words=10), kind=Notification.Kind.ERROR),
        Notification(user=user, message=faker.sentence(nb_words=10), kind=Notification.Kind.PROCESSING),
    ]
    return Notification.objects.bulk_create(list_)
