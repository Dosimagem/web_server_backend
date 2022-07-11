from django.urls import path

from .views import profile

app_name = 'client'
urlpatterns = [
    path('profile/', profile, name='profile'),
]
