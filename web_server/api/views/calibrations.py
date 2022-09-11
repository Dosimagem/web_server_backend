from http import HTTPStatus

from django.contrib.auth import get_user_model
from rest_framework.response import Response
from rest_framework.decorators import (
                                        api_view,
                                        authentication_classes,
                                        permission_classes
                                        )
from rest_framework.permissions import IsAuthenticated

from web_server.service.models import Calibration, Isotope
from web_server.service.forms import CreateCalibrationForm, IsotopeForm, UpdateCalibrationForm

from .utils import MyTokenAuthentication, list_errors
from .errors_msg import MSG_ERROR_USER_CALIBRATIONS, MSG_ERROR_TOKEN_USER, MSG_ERROR_RESOURCE

User = get_user_model()


@api_view(['GET', 'POST'])
@authentication_classes([MyTokenAuthentication])
@permission_classes([IsAuthenticated])
def calibrations_list_create(request, user_id):

    if request.user.uuid != user_id:
        return Response({'errors': MSG_ERROR_TOKEN_USER}, status=HTTPStatus.UNAUTHORIZED)

    dispatcher = {
        'GET': _list_calibrations,
        'POST': _create_calibrations
    }

    view = dispatcher[request.method]

    return view(request, user_id)


@api_view(['DELETE', 'GET', 'PUT'])
@authentication_classes([MyTokenAuthentication])
@permission_classes([IsAuthenticated])
def calibrations_read_update_delete(request, user_id, calibration_id):

    if request.user.uuid != user_id:
        return Response({'errors': MSG_ERROR_TOKEN_USER}, status=HTTPStatus.UNAUTHORIZED)

    dispatcher = {
        'GET': _read_calibration,
        'DELETE': _delete_calibration,
        'PUT': _update_calibration,
    }

    view = dispatcher[request.method]

    return view(request, user_id, calibration_id)


def _read_calibration(request, user_id, calibration_id):

    if cali := Calibration.objects.filter(user__uuid=user_id, uuid=calibration_id).first():
        return Response(data=cali.to_dict())

    return Response(data={'errors': MSG_ERROR_RESOURCE}, status=HTTPStatus.NOT_FOUND)


def _update_calibration(request, user_id, calibration_id):
    if cali := Calibration.objects.filter(user__uuid=user_id, uuid=calibration_id).first():

        # TODO: codigo repetido

        data = request.data

        form_isopote = IsotopeForm(data)

        if not form_isopote.is_valid():
            return Response(data={'errors': list_errors(form_isopote.errors)}, status=HTTPStatus.BAD_REQUEST)

        isotope = Isotope.objects.filter(name=form_isopote.cleaned_data['isotope']).first()

        data['user'] = request.user
        data['isotope'] = isotope

        form = UpdateCalibrationForm(data, request.FILES, instance=cali)

        if not form.is_valid():
            return Response(data={'errors': list_errors(form.errors)}, status=HTTPStatus.BAD_REQUEST)

        for field, value in form.cleaned_data.items():
            if getattr(cali, field) != value:
                setattr(cali, field, value)

        cali.save()

        return Response(status=HTTPStatus.NO_CONTENT)

    return Response(data={'errors': MSG_ERROR_RESOURCE}, status=HTTPStatus.NOT_FOUND)


def _delete_calibration(request, user_id, calibration_id):

    if cali := Calibration.objects.filter(user__uuid=user_id, uuid=calibration_id).first():
        cali.delete()
        return Response(status=HTTPStatus.NO_CONTENT)

    return Response(data={'errors': MSG_ERROR_RESOURCE}, status=HTTPStatus.NOT_FOUND)


def _list_calibrations(request, user_id):
    if calibration := Calibration.objects.filter(user=request.user):

        calibration_list = [q.to_dict() for q in calibration]

        data = {
            'count': len(calibration_list),
            'row': calibration_list
        }

        return Response(data=data)

    data = {'errors': MSG_ERROR_USER_CALIBRATIONS}
    return Response(data=data, status=HTTPStatus.NOT_FOUND)  # TODO: not repat usersself !!


def _create_calibrations(request, user_id):

    data = request.data

    form_isopote = IsotopeForm(data)

    if not form_isopote.is_valid():
        return Response(data={'errors': list_errors(form_isopote.errors)}, status=HTTPStatus.BAD_REQUEST)

    isotope = Isotope.objects.filter(name=form_isopote.cleaned_data['isotope']).first()

    data['user'] = request.user
    data['isotope'] = isotope

    form = CreateCalibrationForm(data, request.FILES)

    if not form.is_valid():
        return Response(data={'errors': list_errors(form.errors)}, status=HTTPStatus.BAD_REQUEST)

    new_calibration = form.save()

    return Response(data=new_calibration.to_dict(), status=HTTPStatus.CREATED)
