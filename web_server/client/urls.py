from django.urls import path

from .views import profile

#  TODO: app namespace
urlpatterns = [
    path('profile/', profile, name='profile'),
]
