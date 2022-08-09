from django.urls import path

from .views import dosimetry_order, profile

app_name = 'client'
urlpatterns = [
    path('profile/', profile, name='profile'),
    path('client/dosimetry_order/', dosimetry_order, name='dosimetry_order'),
]
