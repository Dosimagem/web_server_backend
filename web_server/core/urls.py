from django.urls import path

from .views.register import MyObtainAuthToken, register
from .views.users import email_verify, read_update_email, users_read_update

app_name = 'core'
urlpatterns = [
    path('users/register/', register, name='register'),
    path('users/login/', MyObtainAuthToken.as_view(), name='login'),
    #
    path('users/<uuid:user_id>', users_read_update, name='users-read-update'),
    path('users/<uuid:user_id>/email/', read_update_email, name='read-update-email'),
    path('users/<uuid:user_id>/email/verify/', email_verify, name='email-verify'),
]
