from django.urls import path

from .views import register

app_name = 'api'
urlpatterns = [
    path('register', register, name='register'),
]
