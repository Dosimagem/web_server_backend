from http import HTTPStatus

from django.http import JsonResponse
from django.db import connection


class HealthCheckMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path == '/api/v1/health/':
            with connection.cursor() as cursor:
                try:
                    cursor.execute('SELECT 1+1')
                except Exception as e:
                    return JsonResponse({'status': str(e)}, status=HTTPStatus.INTERNAL_SERVER_ERROR)

            return JsonResponse({'status': 'ok'}, status=HTTPStatus.OK)
        return self.get_response(request)
