from rest_framework.decorators import (
    api_view,
    authentication_classes,
    permission_classes,
)
from rest_framework.response import Response

from web_server.isotope.models import Isotope


@api_view(['GET'])
@authentication_classes([])
@permission_classes([])
def isotope(request):

    queryset = Isotope.objects.all()

    query = request.query_params.get('q')
    if query == 'dosimetry':
        queryset = queryset.filter(dosimetry=True)
    elif query == 'radiosyno':
        queryset = queryset.filter(radiosyno=True)

    isotopes = [i.name for i in queryset]

    data = {'count': len(isotopes), 'row': isotopes}

    return Response(data=data)
