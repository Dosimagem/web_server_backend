from web_server.notification.models import Notification
from web_server.notification.notification_svc import toogle


def test_toogle(notification):

    noti_db = Notification.objects.get(pk=notification.pk)

    assert not noti_db.checked

    toogle(notification)

    noti_db.refresh_from_db()
    assert noti_db.checked

    toogle(notification)

    noti_db.refresh_from_db()
    assert not noti_db.checked
