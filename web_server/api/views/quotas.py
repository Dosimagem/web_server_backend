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
from web_server.service.models import UserQuota
from .utils import MyTokenAuthentication, list_errors


User = get_user_model()


MSG_ERROR_USER_QUOTA = ['This user has no quota record.']
MSG_ERROR_TOKEN_USER = ['Token and User id do not match.']


@api_view(['POST', 'GET'])
@authentication_classes([MyTokenAuthentication])
@permission_classes([IsAuthenticated])
def quotas_list_create(request, user_id):

    if request.user.uuid != user_id:
        return Response({'errors': MSG_ERROR_TOKEN_USER}, status=HTTPStatus.UNAUTHORIZED)

    dispatcher = {
        'POST': _create_quotas,
        'GET': _list_quotas,
    }

    view = dispatcher[request.method]

    return view(request, user_id)


@api_view(['GET', 'PATCH', 'DELETE'])
@authentication_classes([MyTokenAuthentication])
@permission_classes([IsAuthenticated])
def quotas_read_patch_delete(request, user_id, quota_id):

    if request.user.uuid != user_id:
        return Response({'errors': MSG_ERROR_TOKEN_USER}, status=HTTPStatus.UNAUTHORIZED)

    query_set = UserQuota.objects.filter(user__uuid=user_id)

    if not query_set:
        return Response(data={'errors': MSG_ERROR_USER_QUOTA}, status=HTTPStatus.NOT_FOUND)

    quota = query_set.filter(uuid=quota_id).first()
    if not quota:
        return Response(data={'errors': ['There is no information for this pair of ids']}, status=HTTPStatus.NOT_FOUND)

    dispatcher = {
        'DELETE': _delete_quota,
        'GET': _read_quota,
        'PATCH': _update_quota
    }

    view = dispatcher[request.method]

    return view(request, quota)


def _read_quota(request, quota):
    return Response(data=_quota_to_dict(quota))


def _delete_quota(request, quota):
    quota.delete()
    return Response(status=HTTPStatus.NO_CONTENT)


def _update_quota(request, quota):
    form = UpdateQuotasForm(request.data)

    if not form.is_valid():
        return Response(data={'errors': list_errors(form.errors)}, status=HTTPStatus.BAD_REQUEST)

    quota.amount = form.cleaned_data['amount']

    quota.save()

    return Response(status=HTTPStatus.NO_CONTENT)


def _create_quotas(request,  user_id):

    form = CreateQuotasForm(request.data)

    if not form.is_valid():
        return Response(data={'errors': list_errors(form.errors)}, status=HTTPStatus.BAD_REQUEST)

    new_quota = {'user': request.user}

    new_quota.update(form.cleaned_data)

    quota_create = UserQuota.objects.create(**new_quota)

    return Response(data=_quota_to_dict(quota_create), status=HTTPStatus.CREATED)


def _list_quotas(request, user_id):
    if quota := UserQuota.objects.filter(user=request.user):

        quota_list = [_quota_to_dict(q) for q in quota]

        return Response(data={'quotas': quota_list})

    data = {'errors': MSG_ERROR_USER_QUOTA}
    return Response(data=data, status=HTTPStatus.NOT_FOUND)


def _quota_to_dict(quota):
    return {
        'id': quota.uuid,
        'user_id': quota.user.uuid,
        'amount': quota.amount,
        'price': quota.price,
        'service_type': quota.get_service_type_display(),
        'status_payment': quota.get_status_payment_display(),
        'created_at': quota.created_at.date()
    }
