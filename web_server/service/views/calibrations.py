from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from rest_framework.decorators import (
    api_view,
    authentication_classes,
    permission_classes,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from web_server.core.decorators import user_from_token_and_user_from_url
from web_server.core.errors_msg import MSG_ERROR_RESOURCE, list_errors
from web_server.core.views.auth import MyTokenAuthentication
from web_server.service.forms import (
    CreateCalibrationForm,
    IsotopeForm,
    UpdateCalibrationForm,
)
from web_server.service.models import Calibration, DosimetryAnalysisBase, Isotope

User = get_user_model()


@api_view(['GET', 'POST'])
@authentication_classes([MyTokenAuthentication])
@permission_classes([IsAuthenticated])
@user_from_token_and_user_from_url
def calibrations_list_create(request, user_id):

    dispatcher = {'GET': _list_calibrations, 'POST': _create_calibrations}

    view = dispatcher[request.method]

    return view(request, user_id)


@api_view(['DELETE', 'GET', 'PUT'])
@authentication_classes([MyTokenAuthentication])
@permission_classes([IsAuthenticated])
@user_from_token_and_user_from_url
def calibrations_read_update_delete(request, user_id, calibration_id):

    dispatcher = {
        'GET': _read_calibration,
        'DELETE': _delete_calibration,
        'PUT': _update_calibration,
    }

    view = dispatcher[request.method]

    return view(request, user_id, calibration_id)


def _read_calibration(request, user_id, calibration_id):

    if cali := Calibration.objects.filter(user__uuid=user_id, uuid=calibration_id).first():
        return Response(data=cali.to_dict(request))

    return Response(data={'errors': MSG_ERROR_RESOURCE}, status=HTTPStatus.NOT_FOUND)


def _update_calibration(request, user_id, calibration_id):

    try:
        cali = Calibration.objects.get(user__uuid=user_id, uuid=calibration_id)

        # TODO: Colocar isso em uma camada de serviço (Regra de Negocio)

        q = Q(status=DosimetryAnalysisBase.INVALID_INFOS) | Q(status=DosimetryAnalysisBase.DATA_SENT)
        if cali.clinic_dosimetry_analysis.exclude(q).exists() or cali.preclinic_dosimetry_analysis.exclude(q).exists():
            data = {
                'errors': [
                    (
                        'Apenas calibrações associadas com análises com o status '
                        "Informações Inválidas' ou 'Dados Enviados' podem ser atualizadas/deletadas."
                    )
                ]
            }
            return Response(data=data, status=HTTPStatus.CONFLICT)

        # TODO: codigo repetido
        data = request.data

        form_isopote = IsotopeForm(data)

        if not form_isopote.is_valid():
            return Response(
                data={'errors': list_errors(form_isopote.errors)},
                status=HTTPStatus.BAD_REQUEST,
            )

        isotope = Isotope.objects.get(name=form_isopote.cleaned_data['isotope'])

        data['user'] = request.user
        data['isotope'] = isotope

        form = UpdateCalibrationForm(data, request.FILES, instance=cali)

        if not form.is_valid():
            return Response(
                data={'errors': list_errors(form.errors)},
                status=HTTPStatus.BAD_REQUEST,
            )

        cali.save()

        return Response(status=HTTPStatus.NO_CONTENT)

    except ObjectDoesNotExist:
        return Response(data={'errors': MSG_ERROR_RESOURCE}, status=HTTPStatus.NOT_FOUND)


def _delete_calibration(request, user_id, calibration_id):

    try:
        cali = Calibration.objects.get(user__uuid=user_id, uuid=calibration_id)

        # TODO: Colocar isso em uma camada de serviço (Regra de Negocio)
        q = Q(status=DosimetryAnalysisBase.INVALID_INFOS) | Q(status=DosimetryAnalysisBase.DATA_SENT)
        if cali.clinic_dosimetry_analysis.exclude(q).exists() or cali.preclinic_dosimetry_analysis.exclude(q).exists():
            data = {
                'errors': [
                    (
                        'Apenas calibrações associadas com análises com o status '
                        "Informações Inválidas' ou 'Dados Enviados' podem ser atualizadas/deletadas."
                    )
                ]
            }
            return Response(data=data, status=HTTPStatus.CONFLICT)

        cali.delete()
        data = {
            'id': calibration_id,
            'message': 'Calibração deletada com sucesso!',
        }
        return Response(data=data)

    except ObjectDoesNotExist:
        return Response(data={'errors': MSG_ERROR_RESOURCE}, status=HTTPStatus.NOT_FOUND)


def _list_calibrations(request, user_id):

    calibration = Calibration.objects.filter(user=request.user)

    calibration_list = [q.to_dict(request) for q in calibration]

    data = {'count': len(calibration_list), 'row': calibration_list}

    return Response(data=data)


def _create_calibrations(request, user_id):

    data = request.data

    form_isopote = IsotopeForm(data)

    if not form_isopote.is_valid():
        return Response(
            data={'errors': list_errors(form_isopote.errors)},
            status=HTTPStatus.BAD_REQUEST,
        )

    isotope = Isotope.objects.filter(name=form_isopote.cleaned_data['isotope']).first()

    data['user'] = request.user
    data['isotope'] = isotope

    form = CreateCalibrationForm(data=data, files=request.FILES)

    if not form.is_valid():
        return Response(
            data={'errors': list_errors(form.errors)},
            status=HTTPStatus.BAD_REQUEST,
        )

    new_calibration = form.save()

    return Response(data=new_calibration.to_dict(request), status=HTTPStatus.CREATED)
