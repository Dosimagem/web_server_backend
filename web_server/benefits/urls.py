from django.urls import path

from .views import benefit_list, benefit_read

app_name = 'benefits'
urlpatterns = [
    path('users/<uuid:user_id>/benefits/', benefit_list, name='benefit-list'),
    path(
        'users/<uuid:user_id>/benefits/<uuid:benefit_id>',
        benefit_read,
        name='benefit-read',
    ),
]
