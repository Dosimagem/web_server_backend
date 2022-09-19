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


from web_server.service.forms import ClinicDosimetryAnalysisCreateForm
from web_server.service.models import ClinicDosimetryAnalysis, Order, Calibration
from web_server.api.forms import ClinicDosimetryAnalysisCreateFormApi
from .auth import MyTokenAuthentication
from .errors_msg import (
    MSG_ERROR_TOKEN_USER,
    list_errors
)


@api_view(['GET', 'POST'])
@authentication_classes([MyTokenAuthentication])
@permission_classes([IsAuthenticated])
def analysis_list_create(request, user_id, order_id):

    if request.user.uuid != user_id:
        return Response({'errors': MSG_ERROR_TOKEN_USER}, status=HTTPStatus.UNAUTHORIZED)

    dispatcher = {
        'GET': _list_analysis,
        'POST': _create_analysis
    }

    view = dispatcher[request.method]

    return view(request, user_id, order_id)


def _list_analysis(request, user_id, order_id):

    list_ = ClinicDosimetryAnalysis.objects.filter(user__uuid=user_id, order__uuid=order_id)

    data = {
        'count': len(list_),
        'row': [a.to_dict() for a in list_]
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
        return Response({'errors': ['Todas as análises para essa pedido já foram usuadas.']},
                        status=HTTPStatus.CONFLICT)

    try:
        calibration = Calibration.objects.get(uuid=form.cleaned_data['calibration_id'])
    except ObjectDoesNotExist:
        return Response(data={'errors': ['Calibração com esse id não existe.']}, status=HTTPStatus.BAD_REQUEST)

    data = {'user': user, 'order': order, 'calibration': calibration}

    form_clinic_dosi = ClinicDosimetryAnalysisCreateForm(data, request.FILES)

    if not form_clinic_dosi.is_valid():
        return Response({'errors': list_errors(form_clinic_dosi.errors)}, status=HTTPStatus.BAD_REQUEST)

    with transaction.atomic():
        order.remaining_of_analyzes -= 1
        order.save()
        new_clinic_dosi = form_clinic_dosi.save()

    return Response(new_clinic_dosi.to_dict(), status=HTTPStatus.CREATED)
