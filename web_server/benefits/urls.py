from django.urls import path

from .views import benefit_read

app_name = 'benefits'
urlpatterns = [
    # path('users/<uuid:user_id>/benefits/', benefit_list, name='benefit-list'),
    path('users/<uuid:user_id>/signatures/', benefit_read, name='benefit-read'),
]
