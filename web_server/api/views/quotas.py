from http import HTTPStatus

from django.contrib.auth import get_user_model
from rest_framework.response import Response
from rest_framework.decorators import (
                                        api_view,
                                        authentication_classes,
                                        permission_classes
                                        )
from rest_framework.permissions import IsAuthenticated

from web_server.service.forms import CreateQuotasForm
from web_server.service.models import UserQuota
from .utils import MyTokenAuthentication, list_errors


User = get_user_model()


MSG_ERROR = ['This user has no quota record.']


@api_view(['POST', 'GET', 'PATCH', 'DELETE'])
@authentication_classes([MyTokenAuthentication])
@permission_classes([IsAuthenticated])
def quotas(request, user_id):

    if request.user.uuid != user_id:
        return Response({'errors': ['Token and User id do not match.']}, status=HTTPStatus.UNAUTHORIZED)

    dispatcher = {
        'POST': _create_quotas,
        'GET': _read_quotas,
        'PATCH': _update_quotas,
        'DELETE': _delete_quotas,
    }

    view = dispatcher[request.method]

    return view(request, user_id)


def _delete_quotas(request, user_id):

    if quota := UserQuota.objects.filter(user=request.user).first():
        quota.delete()
        return Response(status=HTTPStatus.NO_CONTENT)

    data = {'errors': MSG_ERROR}
    return Response(data=data, status=HTTPStatus.NOT_FOUND)


def _update_quotas(request, user_id):
    form = CreateQuotasForm(request.data)
    if not form.is_valid():
        return Response(data={'errors': list_errors(form.errors)}, status=HTTPStatus.BAD_REQUEST)

    if quota := UserQuota.objects.filter(user=request.user).first():
        quota.clinic_dosimetry = form.cleaned_data['clinic_dosimetry']
        quota.save()
        return Response(status=HTTPStatus.NO_CONTENT)

    data = {'errors': MSG_ERROR}
    return Response(data=data, status=HTTPStatus.NOT_FOUND)


def _create_quotas(request,  user_id):

    form = CreateQuotasForm(request.data)

    if not form.is_valid():
        return Response(data={'errors': list_errors(form.errors)}, status=HTTPStatus.BAD_REQUEST)

    new_quota = {'user': request.user}

    new_quota.update(form.cleaned_data)

    quota_create = UserQuota.objects.create(**new_quota)

    return Response(data=_quota_to_dict(quota_create), status=HTTPStatus.CREATED)


def _read_quotas(request, user_id):
    if quota := UserQuota.objects.filter(user=request.user):

        quota_list = [_quota_to_dict(q) for q in quota ]

        return Response(data={'quotas': quota_list})

    data = {'errors': MSG_ERROR}
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
