from django.urls import path

from .views import register, MyObtainAuthToken, users

app_name = 'api'
urlpatterns = [
    path('register/', register, name='register'),
    path('login/',  MyObtainAuthToken.as_view(), name='login'),
    path('users/<uuid:id>', users, name='users')
]
