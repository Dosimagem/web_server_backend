from django.urls import path

from .views import send_email

app_name = 'budget'
urlpatterns = [
    path('users/<uuid:user_id>/budget/', send_email, name='send_email'),
]
