from django.urls import path

from .views import register, MyObtainAuthToken

app_name = 'api'
urlpatterns = [
    path('register/', register, name='register'),
    path('login/',  MyObtainAuthToken.as_view(), name='login')
]
