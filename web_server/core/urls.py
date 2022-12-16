from django.urls import path

from .views.auth import (
    MyLoginView,
    MyLogoutView,
    MyRefreshViewWithCookieSupport,
    am_i_auth,
    change_password,
    reset_password,
)
from .views.register import register
from .views.users import (
    email_resend,
    email_verify,
    read_update_email,
    users_read_update,
)

app_name = 'core'
urlpatterns = [
    # auth
    path('whoima/', am_i_auth, name='am-i-auth'),
    path('users/register/', register, name='register'),
    path('users/login/', MyLoginView.as_view(), name='login'),
    path('users/auth/reset_password/', reset_password, name='reset-password'),
    path('users/auth/token/logout/', MyLogoutView.as_view(), name='logout'),
    path('users/auth/token/refresh/', MyRefreshViewWithCookieSupport.as_view(), name='refresh-token'),
    path('users/<uuid:user_id>/change_password/', change_password, name='change-password'),
    # user info
    path('users/<uuid:user_id>', users_read_update, name='users-read-update'),
    path('users/<uuid:user_id>/email/', read_update_email, name='read-update-email'),
    path('users/<uuid:user_id>/email/verify/', email_verify, name='email-verify'),
    path('users/<uuid:user_id>/email/resend/', email_resend, name='email-resend'),
]
