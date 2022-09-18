from http  import HTTPStatus

from rest_framework.response import Response
from rest_framework.decorators import (
    api_view,
    authentication_classes,
    permission_classes
)
from rest_framework.permissions import IsAuthenticated
from django.core.exceptions import ObjectDoesNotExist


from web_server.service.forms import ClinicDosimetryAnalysisCreateForm
from web_server.service.models import Order, Calibration
from web_server.api.forms import ClinicDosimetryAnalysisCreateFormApi
from .auth import MyTokenAuthentication
from .errors_msg import (
    MSG_ERROR_TOKEN_USER,
    list_errors
)


@api_view(['POST'])
@authentication_classes([MyTokenAuthentication])
@permission_classes([IsAuthenticated])
def clinic_dosimetry_list_create(request, user_id, order_id):

    if request.user.uuid != user_id:
        return Response({'errors': MSG_ERROR_TOKEN_USER}, status=HTTPStatus.UNAUTHORIZED)

    dispatcher = {
        # 'GET': _list_calibrations,
        'POST': _create_clinic_dosimetry_analysis
    }

    view = dispatcher[request.method]

    return view(request, user_id, order_id)


def _create_clinic_dosimetry_analysis(request, user_id, order_id):

    data = request.data

    form = ClinicDosimetryAnalysisCreateFormApi(data)

    if not form.is_valid():
        return Response(data={'errors': list_errors(form.errors)}, status=HTTPStatus.BAD_REQUEST)

    user = request.user

    try:
        order = Order.objects.get(user=user, uuid=order_id)
    except ObjectDoesNotExist:
        return Response(status=HTTPStatus.NOT_FOUND)

    try:
        calibration = Calibration.objects.get(uuid=form.cleaned_data['calibration_id'])
    except ObjectDoesNotExist:
        return Response(data={'errors': ['Calibração com esse id não existe.']}, status=HTTPStatus.BAD_REQUEST)


    data = {
        'user': user,
        'order': order,
        'calibration': calibration
    }

    form_clinic_dosi = ClinicDosimetryAnalysisCreateForm(data, request.FILES)

    if not form_clinic_dosi.is_valid():
        return

    new_clinic_dosi = form_clinic_dosi.save()

    return Response(new_clinic_dosi.to_dict(), status=HTTPStatus.CREATED)
