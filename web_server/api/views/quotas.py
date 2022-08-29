from http import HTTPStatus

from django.contrib.auth import get_user_model
from rest_framework.response import Response
from rest_framework.decorators import (
                                        api_view,
                                        authentication_classes,
                                        permission_classes
                                        )
from rest_framework.permissions import IsAuthenticated

from web_server.service.forms import QuotasForm
from web_server.service.models import UserQuotas
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

    if quota := UserQuotas.objects.filter(user=request.user).first():
        quota.delete()
        return Response(status=HTTPStatus.NO_CONTENT)

    data = {'errors': MSG_ERROR}
    return Response(data=data, status=HTTPStatus.NOT_FOUND)


def _update_quotas(request, user_id):
    form = QuotasForm(request.data)
    if not form.is_valid():
        return Response(data={'errors': list_errors(form.errors)}, status=HTTPStatus.BAD_REQUEST)

    if quota := UserQuotas.objects.filter(user=request.user).first():
        quota.clinic_dosimetry = form.cleaned_data['clinic_dosimetry']
        quota.save()
        return Response(status=HTTPStatus.NO_CONTENT)

    data = {'errors': MSG_ERROR}
    return Response(data=data, status=HTTPStatus.NOT_FOUND)


def _create_quotas(request,  user_id):

    payload = {
        'clinic_dosimetry': request.data.get('clinic_dosimetry', 0)
    }

    form = QuotasForm(payload)
    if not form.is_valid():
        return Response(data={'errors': list_errors(form.errors)}, status=HTTPStatus.BAD_REQUEST)

    new_quotas = {
        'user': request.user,
        'clinic_dosimetry': form.cleaned_data['clinic_dosimetry']
    }

    if UserQuotas.objects.filter(user=request.user):
        return Response(data={'errors': ['This user already have quota register']}, status=HTTPStatus.BAD_REQUEST)

    quotas_create = UserQuotas.objects.create(**new_quotas)

    data = {
        'id': quotas_create.uuid,
        'clinic_dosimetry': quotas_create.clinic_dosimetry
    }

    return Response(data=data, status=HTTPStatus.CREATED)


def _read_quotas(request, user_id):
    if quota := UserQuotas.objects.filter(user=request.user).first():
        return Response(data={'clinic_dosimetry': quota.clinic_dosimetry})

    data = {'errors': MSG_ERROR}
    return Response(data=data, status=HTTPStatus.NOT_FOUND)
