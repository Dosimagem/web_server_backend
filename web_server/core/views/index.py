from django.http import JsonResponse
from django.utils.translation import gettext as _
from rest_framework.decorators import authentication_classes, permission_classes


@authentication_classes([])
@permission_classes([])
def index(request):
    return JsonResponse({'message': _('Welcome to Dosiamge API !')})
