from http import HTTPStatus

from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from rest_framework.decorators import api_view
from rest_framework.response import Response

from web_server.core.decorators import user_from_token_and_user_from_url
from web_server.core.errors_msg import (
    ERROR_CALIBRATION_ID,
    MSG_ERROR_RESOURCE,
    list_errors,
)
from web_server.service.analysis_svc import AnalisysChoice
from web_server.service.forms import (
    PreClinicAndClinicDosimetryAnalysisCreateFormApi,
    PreClinicAndClinicDosimetryAnalysisUpdateFormApi,
    RadiosynoAnalysisCreateFormApi,
)
from web_server.service.models import Calibration, Isotope, Order
from web_server.service.order_svc import OrderInfos


@api_view(['GET', 'DELETE', 'PUT'])
@user_from_token_and_user_from_url
def analysis_read_update_delete(request, user_id, order_id, analysis_id):

    dispatcher = {
        'GET': _read_analysis,
        'DELETE': _delete_analysis,
        'PUT': _update_analysis,
    }

    view = dispatcher[request.method]

    return view(request, user_id, order_id, analysis_id)


@api_view(['GET', 'POST'])
@user_from_token_and_user_from_url
def analysis_list_create(request, user_id, order_id):

    dispatcher = {'GET': _list_analysis, 'POST': _create_analysis}

    view = dispatcher[request.method]

    return view(request, user_id, order_id)


def _delete_analysis(request, user_id, order_id, analysis_id):

    try:
        order = Order.objects.get(user__uuid=user_id, uuid=order_id)
        Model = AnalisysChoice(order=order).model
        analysis = Model.objects.get(uuid=analysis_id, order=order)
    except ObjectDoesNotExist:
        return Response(data={'errors': MSG_ERROR_RESOURCE}, status=HTTPStatus.NOT_FOUND)

    # TODO: Colocar isso em uma camada de serviço
    # if analysis.status in [Model.INVALID_INFOS, Model.DATA_SENT]:
    if analysis.status == Model.INVALID_INFOS or analysis.status == Model.DATA_SENT:
        analysis.delete()
        order.remaining_of_analyzes += 1
        order.save()
    else:
        msg = ['Não foi possivel deletar essa análise.']
        return Response(data={'errors': msg}, status=HTTPStatus.CONFLICT)

    data = {'id': analysis_id, 'message': 'Análise deletada com sucesso!'}

    return Response(data=data)


def _read_analysis(request, user_id, order_id, analysis_id):

    try:
        order = Order.objects.get(user__uuid=user_id, uuid=order_id)
        Model = AnalisysChoice(order=order).model
        analysis = Model.objects.get(uuid=analysis_id, order=order)
    except ObjectDoesNotExist:
        return Response(data={'errors': MSG_ERROR_RESOURCE}, status=HTTPStatus.NOT_FOUND)

    return Response(data=analysis.to_dict(request))


def _list_analysis(request, user_id, order_id):

    try:
        order = Order.objects.get(user__uuid=user_id, uuid=order_id)
    except ObjectDoesNotExist:
        return Response(status=HTTPStatus.NOT_FOUND)

    Model = AnalisysChoice(order=order).model
    list_ = Model.objects.filter(order=order)

    data = {'count': len(list_), 'row': [a.to_dict(request) for a in list_]}

    return Response(data)


def _update_analysis(request, user_id, order_id, analysis_id):

    data = request.data

    user = request.user

    try:
        order = Order.objects.get(user=user, uuid=order_id)
    except ObjectDoesNotExist:
        return Response(data={'errors': MSG_ERROR_RESOURCE}, status=HTTPStatus.NOT_FOUND)

    # TODO: Codigo repetido com o update
    if order.service_name == Order.PRECLINIC_DOSIMETRY or order.service_name == Order.CLINIC_DOSIMETRY:

        form = PreClinicAndClinicDosimetryAnalysisUpdateFormApi(data)

        if not form.is_valid():
            return Response(data={'errors': list_errors(form.errors)}, status=HTTPStatus.BAD_REQUEST)

        try:
            calibration = Calibration.objects.get(uuid=form.cleaned_data['calibration_id'], user=user)
        except ObjectDoesNotExist:
            return Response(data={'errors': ERROR_CALIBRATION_ID}, status=HTTPStatus.NOT_FOUND)

        data['calibration'] = calibration

    elif order.service_name == Order.RADIOSYNOVIORTHESIS:

        form = RadiosynoAnalysisCreateFormApi(data)

        if not form.is_valid():
            return Response(data={'errors': list_errors(form.errors)}, status=HTTPStatus.BAD_REQUEST)

        isotope = Isotope.objects.get(name=form.cleaned_data['isotope'])

        data['isotope'] = isotope

    data['order'] = order

    analisys_choice = AnalisysChoice(order=order)

    try:
        Model = analisys_choice.model
        analysis = Model.objects.get(uuid=analysis_id, order=order)
    except ObjectDoesNotExist:
        return Response(data={'errors': MSG_ERROR_RESOURCE}, status=HTTPStatus.NOT_FOUND)

    if analysis.status not in (Model.INVALID_INFOS, Model.DATA_SENT):
        msg = ['Não foi possivel atualizar essa análise.']
        return Response(data={'errors': msg}, status=HTTPStatus.CONFLICT)

    AnalysisForm = analisys_choice.update_form
    form_analysis = AnalysisForm(data, request.FILES, instance=analysis)

    if not form_analysis.is_valid():
        return Response(data={'errors': list_errors(form_analysis.errors)}, status=HTTPStatus.BAD_REQUEST)

    form_analysis.change_status_and_save()

    return Response(status=HTTPStatus.NO_CONTENT)


def _create_analysis(request, user_id, order_id):

    data = request.data

    user = request.user

    try:
        order = Order.objects.get(user=user, uuid=order_id)
    except ObjectDoesNotExist:
        return Response(status=HTTPStatus.NOT_FOUND)

    order_infos = OrderInfos(order)

    if not order_infos.are_analyzes_available():
        return Response({'errors': ['Todas as análises para essa pedido já foram usadas.']}, status=HTTPStatus.CONFLICT)

    if not order_infos.has_payment_confirmed():
        return Response({'errors': ['O pagamento desse pedido não foi confirmado.']}, status=HTTPStatus.CONFLICT)

    # TODO: Codigo repetido com o update
    if order.service_name == Order.PRECLINIC_DOSIMETRY or order.service_name == Order.CLINIC_DOSIMETRY:

        form = PreClinicAndClinicDosimetryAnalysisCreateFormApi(data)

        if not form.is_valid():
            return Response(data={'errors': list_errors(form.errors)}, status=HTTPStatus.BAD_REQUEST)

        try:
            calibration = Calibration.objects.get(uuid=form.cleaned_data['calibration_id'], user__uuid=user_id)
        except ObjectDoesNotExist:
            return Response(data={'errors': ERROR_CALIBRATION_ID}, status=HTTPStatus.BAD_REQUEST)

        data['calibration'] = calibration

    elif order.service_name == Order.RADIOSYNOVIORTHESIS:

        form = RadiosynoAnalysisCreateFormApi(data)

        if not form.is_valid():
            return Response(data={'errors': list_errors(form.errors)}, status=HTTPStatus.BAD_REQUEST)

        isotope = Isotope.objects.get(name=form.cleaned_data['isotope'])

        data['isotope'] = isotope

    data['order'] = order

    AnalysisFormClass = AnalisysChoice(order=order).create_form
    form_analysis = AnalysisFormClass(data, request.FILES)

    if not form_analysis.is_valid():
        return Response({'errors': list_errors(form_analysis.errors)}, status=HTTPStatus.BAD_REQUEST)

    with transaction.atomic():
        # TODO: Colocar isso em uma camada de serviço
        order.remaining_of_analyzes -= 1
        order.save()
        new_analysis = form_analysis.save()

    return Response(new_analysis.to_dict(request), status=HTTPStatus.CREATED)
