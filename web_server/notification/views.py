from http import HTTPStatus

from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view
from rest_framework.response import Response

from web_server.core.decorators import user_from_token_and_user_from_url
from web_server.notification.models import Notification
from web_server.notification.notification_svc import toogle


@api_view(['GET'])
@user_from_token_and_user_from_url
def notification_list(request, user_id):

    notifications = Notification.objects.all()

    data = {'count': len(notifications), 'row': [noti.to_dict() for noti in notifications]}

    return Response(data=data)


@api_view(['POST'])
@user_from_token_and_user_from_url
def toogle_check(request, user_id, notification_id):

    notification = get_object_or_404(Notification, uuid=notification_id)

    toogle(notification)

    return Response(status=HTTPStatus.NO_CONTENT)
