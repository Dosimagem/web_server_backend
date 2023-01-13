from django.http import JsonResponse
from rest_framework.decorators import authentication_classes, permission_classes
from django.utils.translation import gettext as _


@authentication_classes([])
@permission_classes([])
def index(request):
    return JsonResponse({'message': _('Welcome to Dosiamge API !')})
