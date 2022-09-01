from http import HTTPStatus

from django.contrib.auth import get_user_model
from rest_framework.response import Response
from rest_framework.decorators import (
                                        api_view,
                                        authentication_classes,
                                        permission_classes
                                        )
from rest_framework.permissions import IsAuthenticated

from web_server.service.forms import CreateQuotasForm, UpdateQuotasForm
from web_server.service.models import Order
from .utils import MyTokenAuthentication, list_errors


User = get_user_model()


MSG_ERROR_USER_QUOTA = ['This user has no order record.']
MSG_ERROR_TOKEN_USER = ['Token and User id do not match.']


@api_view(['POST', 'GET'])
@authentication_classes([MyTokenAuthentication])
@permission_classes([IsAuthenticated])
def orders_list_create(request, user_id):

    if request.user.uuid != user_id:
        return Response({'errors': MSG_ERROR_TOKEN_USER}, status=HTTPStatus.UNAUTHORIZED)

    dispatcher = {
        'POST': _create_orders,
        'GET': _list_orders,
    }

    view = dispatcher[request.method]

    return view(request, user_id)


@api_view(['GET', 'PATCH', 'DELETE'])
@authentication_classes([MyTokenAuthentication])
@permission_classes([IsAuthenticated])
def orders_read_patch_delete(request, user_id, order_id):

    if request.user.uuid != user_id:
        return Response({'errors': MSG_ERROR_TOKEN_USER}, status=HTTPStatus.UNAUTHORIZED)

    query_set = Order.objects.filter(user__uuid=user_id)

    if not query_set:
        return Response(data={'errors': MSG_ERROR_USER_QUOTA}, status=HTTPStatus.NOT_FOUND)

    order = query_set.filter(uuid=order_id).first()
    if not order:
        return Response(data={'errors': ['There is no information for this pair of ids']}, status=HTTPStatus.NOT_FOUND)

    dispatcher = {
        'DELETE': _delete_order,
        'GET': _read_order,
        'PATCH': _update_order
    }

    view = dispatcher[request.method]

    return view(request, order)


def _read_order(request, order):
    return Response(data=_order_to_dict(order))


def _delete_order(request, order):
    order.delete()
    return Response(status=HTTPStatus.NO_CONTENT)


def _update_order(request, order):
    form = UpdateQuotasForm(request.data)

    if not form.is_valid():
        return Response(data={'errors': list_errors(form.errors)}, status=HTTPStatus.BAD_REQUEST)

    order.amount = form.cleaned_data['amount']

    order.save()

    return Response(status=HTTPStatus.NO_CONTENT)


def _create_orders(request,  user_id):

    form = CreateQuotasForm(request.data)

    if not form.is_valid():
        return Response(data={'errors': list_errors(form.errors)}, status=HTTPStatus.BAD_REQUEST)

    new_order = {'user': request.user}

    new_order.update(form.cleaned_data)

    order_create = Order.objects.create(**new_order)

    return Response(data=_order_to_dict(order_create), status=HTTPStatus.CREATED)


def _list_orders(request, user_id):
    if order := Order.objects.filter(user=request.user):

        order_list = [_order_to_dict(q) for q in order]

        return Response(data={'orders': order_list})

    data = {'errors': MSG_ERROR_USER_QUOTA}
    return Response(data=data, status=HTTPStatus.NOT_FOUND)


def _order_to_dict(order):
    return {
        'id': order.uuid,
        'user_id': order.user.uuid,
        'amount': order.amount,
        'price': order.price,
        'service_type': order.get_service_type_display(),
        'status_payment': order.get_status_payment_display(),
        'created_at': order.created_at.date()
    }
