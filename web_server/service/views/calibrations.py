from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.utils.translation import gettext as _
from rest_framework.decorators import api_view
from rest_framework.response import Response

from web_server.core.decorators import user_from_token_and_user_from_url
from web_server.core.errors_msg import MSG_ERROR_RESOURCE, list_errors
from web_server.isotope.forms import IsotopeDosimetryForm
from web_server.service.forms import CreateCalibrationForm, UpdateCalibrationForm
from web_server.service.models import Calibration, DosimetryAnalysisBase, Isotope

User = get_user_model()


@api_view(['GET', 'POST'])
@user_from_token_and_user_from_url
def calibrations_list_create(request, user_id):

    dispatcher = {'GET': _list_calibrations, 'POST': _create_calibrations}

    view = dispatcher[request.method]

    return view(request, user_id)


@api_view(['DELETE', 'GET', 'PUT'])
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

        q = Q(status=DosimetryAnalysisBase.Status.INVALID_INFOS) | Q(status=DosimetryAnalysisBase.Status.DATA_SENT)
        if cali.clinic_dosimetry_analysis.exclude(q).exists() or cali.preclinic_dosimetry_analysis.exclude(q).exists():
            invalid_infos, data_sent = (
                DosimetryAnalysisBase.Status.INVALID_INFOS.label,
                DosimetryAnalysisBase.Status.DATA_SENT.label,
            )
            data = {
                'errors': [
                    (
                        _('Only calibrations associated with analyzes with the ')
                        + _("status '%(invalid_infos)s' or '%(data_sent)s' can be updated/deleted.")
                        % {'invalid_infos': invalid_infos, 'data_sent': data_sent}
                    )
                ]
            }
            return Response(data=data, status=HTTPStatus.CONFLICT)

        # TODO: codigo repetido
        data = request.data

        form_isopote = IsotopeDosimetryForm(data)

        if not form_isopote.is_valid():
            return Response(data={'errors': list_errors(form_isopote.errors)}, status=HTTPStatus.BAD_REQUEST)

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
        q = Q(status=DosimetryAnalysisBase.Status.INVALID_INFOS) | Q(status=DosimetryAnalysisBase.Status.DATA_SENT)
        if cali.clinic_dosimetry_analysis.exclude(q).exists() or cali.preclinic_dosimetry_analysis.exclude(q).exists():
            invalid_infos, data_sent = (
                DosimetryAnalysisBase.Status.INVALID_INFOS.label,
                DosimetryAnalysisBase.Status.DATA_SENT.label,
            )
            data = {
                'errors': [
                    (
                        _('Only calibrations associated with analyzes with the ')
                        + _("status '%(invalid_infos)s' or '%(data_sent)s' can be updated/deleted.")
                        % {'invalid_infos': invalid_infos, 'data_sent': data_sent}
                    )
                ]
            }

            return Response(data=data, status=HTTPStatus.CONFLICT)

        cali.delete()
        data = {
            'id': calibration_id,
            'message': _('Calibration successfully deleted!'),
        }
        return Response(data=data)

    except ObjectDoesNotExist:
        return Response(data={'errors': MSG_ERROR_RESOURCE}, status=HTTPStatus.NOT_FOUND)


def _list_calibrations(request, user_id):

    # TODO:
    # select_related('user', 'isotope')

    calibration = Calibration.objects.filter(user=request.user)

    calibration_list = [q.to_dict(request) for q in calibration]

    data = {'count': len(calibration_list), 'row': calibration_list}

    return Response(data=data)


def _create_calibrations(request, user_id):

    data = request.data

    form_isopote = IsotopeDosimetryForm(data)

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
        return Response(data={'errors': list_errors(form.errors)}, status=HTTPStatus.BAD_REQUEST)

    new_calibration = form.save()

    headers = {'Location': new_calibration.get_absolute_url()}

    return Response(data=new_calibration.to_dict(request), status=HTTPStatus.CREATED, headers=headers)
