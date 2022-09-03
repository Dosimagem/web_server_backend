from rest_framework.response import Response
from rest_framework.decorators import api_view


from web_server.service.models import Isotope


@api_view(['GET'])
def isotope(request):

    isotopes = _isotope_to_list()

    data = {'count': len(isotopes), 'isotopes': isotopes}

    return Response(data=data)


def _isotope_to_list():
    return [i.name for i in Isotope.objects.all()]
