from django.http import JsonResponse
from rest_framework.decorators import authentication_classes, permission_classes


@authentication_classes([])
@permission_classes([])
def index(request):
    return JsonResponse({'message': 'Welcome to Dosiamge API !'})
