from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.response import Response
from rest_framework.decorators import (
                                        api_view,
                                        authentication_classes,
                                        permission_classes
                                        )
from rest_framework.permissions import IsAuthenticated

from web_server.api.decorators import user_from_token_and_user_from_url
from web_server.service.models import Order
from web_server.service.order_svc import order_to_dict
from .auth import MyTokenAuthentication
from web_server.core.errors_msg import MSG_ERROR_RESOURCE

User = get_user_model()


@api_view(['GET'])
@authentication_classes([MyTokenAuthentication])
@permission_classes([IsAuthenticated])
@user_from_token_and_user_from_url
def orders_list(request, user_id):

    dispatcher = {
        'GET': _list_orders,
    }

    view = dispatcher[request.method]

    return view(request, user_id)


@api_view(['GET'])
@authentication_classes([MyTokenAuthentication])
@permission_classes([IsAuthenticated])
@user_from_token_and_user_from_url
def orders_read(request, user_id, order_id):

    try:
        order = Order.objects.filter(user__uuid=user_id, uuid=order_id).get()
    except ObjectDoesNotExist:
        return Response(data={'errors': MSG_ERROR_RESOURCE}, status=HTTPStatus.NOT_FOUND)

    dispatcher = {
        'GET': _read_order,
    }

    view = dispatcher[request.method]

    return view(request, order)


def _read_order(request, order):
    return Response(data=order_to_dict(order))


def _list_orders(request, user_id):

    order = Order.objects.filter(user=request.user)

    order_list = [order_to_dict(q) for q in order]

    data = {'count': len(order_list), 'row': order_list}

    return Response(data)
