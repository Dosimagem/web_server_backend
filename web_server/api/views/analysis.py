from http import HTTPStatus

from django.db import transaction
from rest_framework.response import Response
from rest_framework.decorators import (
    api_view,
    authentication_classes,
    permission_classes
)
from rest_framework.permissions import IsAuthenticated
from django.core.exceptions import ObjectDoesNotExist

from web_server.api.decorators import user_from_token_and_user_from_url
from web_server.service.forms import ClinicDosimetryAnalysisCreateForm, PreClinicDosimetryAnalysisCreateForm
from web_server.service.models import ClinicDosimetryAnalysis, Order, Calibration, PreClinicDosimetryAnalysis
from web_server.api.forms import ClinicDosimetryAnalysisCreateFormApi
from .auth import MyTokenAuthentication
from .errors_msg import list_errors


@api_view(['GET', 'POST'])
@authentication_classes([MyTokenAuthentication])
@permission_classes([IsAuthenticated])
@user_from_token_and_user_from_url
def analysis_list_create(request, user_id, order_id):

    dispatcher = {
        'GET': _list_analysis,
        'POST': _create_analysis
    }

    view = dispatcher[request.method]

    return view(request, user_id, order_id)


def _list_analysis(request, user_id, order_id):

    try:
        order = Order.objects.get(user__uuid=user_id, uuid=order_id)
    except ObjectDoesNotExist:
        return Response(status=HTTPStatus.NOT_FOUND)

    if order.service_name == Order.PRECLINIC_DOSIMETRY:
        list_ = PreClinicDosimetryAnalysis.objects.filter(user__uuid=user_id, order__uuid=order_id)
    elif order.service_name == Order.CLINIC_DOSIMETRY:
        list_ = ClinicDosimetryAnalysis.objects.filter(user__uuid=user_id, order__uuid=order_id)

    data = {
        'count': len(list_),
        'row': [a.to_dict(request) for a in list_]
    }

    return Response(data)


def _create_analysis(request, user_id, order_id):

    data = request.data

    form = ClinicDosimetryAnalysisCreateFormApi(data)

    if not form.is_valid():
        return Response(data={'errors': list_errors(form.errors)}, status=HTTPStatus.BAD_REQUEST)

    user = request.user

    try:
        order = Order.objects.get(user=user, uuid=order_id)
    except ObjectDoesNotExist:
        return Response(status=HTTPStatus.NOT_FOUND)

    if not order.is_analysis_available():  # TODO: Regra de negocio no modelo não parece uma boa ideia para mim
        return Response({'errors': ['Todas as análises para essa pedido já foram usadas.']},
                        status=HTTPStatus.CONFLICT)

    if order.service_name == Order.PRECLINIC_DOSIMETRY or order.service_name == Order.CLINIC_DOSIMETRY:

        try:
            calibration = Calibration.objects.get(uuid=form.cleaned_data['calibration_id'], user__uuid=user_id)
        except ObjectDoesNotExist:
            return Response(data={'errors': ['Calibração com esse id não existe para esse usuário.']},
                            status=HTTPStatus.BAD_REQUEST)

        data.update({'user': user, 'order': order, 'calibration': calibration})

        if order.service_name == Order.CLINIC_DOSIMETRY:
            form_analysis = ClinicDosimetryAnalysisCreateForm(data, request.FILES)
        elif order.service_name == Order.PRECLINIC_DOSIMETRY:
            form_analysis = PreClinicDosimetryAnalysisCreateForm(data, request.FILES)

        if not form_analysis.is_valid():
            return Response({'errors': list_errors(form_analysis.errors)}, status=HTTPStatus.BAD_REQUEST)

        with transaction.atomic():
            order.remaining_of_analyzes -= 1
            order.save()
            new_analysis = form_analysis.save()

        return Response(new_analysis.to_dict(request), status=HTTPStatus.CREATED)
