from http import HTTPStatus

from django.http import JsonResponse


class HealthCheckMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path == '/api/v1/health/':
            return JsonResponse({'status': 'ok'}, status=HTTPStatus.OK)
        return self.get_response(request)
