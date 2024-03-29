from http import HTTPStatus

from rest_framework.decorators import api_view
from rest_framework.response import Response

from web_server.core.decorators import user_from_token_and_user_from_url
from web_server.core.errors_msg import list_errors
from web_server.radiosynoviorthesis.calculator import radiosysnoviorthesis
from web_server.radiosynoviorthesis.forms import CalculatorForm


@api_view(['POST'])
@user_from_token_and_user_from_url
def calulator_radiosynoviorthesis(request, user_id):

    data = request.data

    form = CalculatorForm(data)

    if not form.is_valid():
        return Response(data={'errors': list_errors(form.errors)}, status=HTTPStatus.BAD_REQUEST)

    data = radiosysnoviorthesis(**form.cleaned_data)

    return Response(data)
