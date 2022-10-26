from rest_framework.decorators import (
    api_view,
    authentication_classes,
    permission_classes,
)
from rest_framework.response import Response

from web_server.service.models import Isotope


@api_view(['GET'])
@authentication_classes([])
@permission_classes([])
def isotope(request):

    isotopes = _isotope_to_list()

    data = {'count': len(isotopes), 'row': isotopes}

    return Response(data=data)


def _isotope_to_list():
    return [i.name for i in Isotope.objects.all()]
