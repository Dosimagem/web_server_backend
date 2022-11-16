from django.urls import path

from .views import notification_list, toogle_check

app_name = 'notification'
urlpatterns = [
    path('users/<uuid:user_id>/notifications/', notification_list, name='notification-list'),
    path('users/<uuid:user_id>/notifications/<uuid:notification_id>/toogle_check/', toogle_check, name='toogle-check'),
]
