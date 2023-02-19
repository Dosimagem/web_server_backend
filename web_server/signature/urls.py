from django.urls import path

from .views import signature_list_create, signature_read

app_name = 'signatures'
urlpatterns = [
    path('users/<uuid:user_id>/signatures/', signature_list_create, name='signature-list-create'),
    path('users/<uuid:user_id>/signatures/<uuid:signature_id>/', signature_read, name='signature-read'),
]
