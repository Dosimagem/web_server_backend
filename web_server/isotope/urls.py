from django.urls import path

from .views import isotope

app_name = 'isotopes'
urlpatterns = [
    #
    path('isotopes/', isotope, name='isotopes-list'),
    #
]
