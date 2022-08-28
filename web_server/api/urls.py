from django.urls import path

from .views import register, MyObtainAuthToken, users, quotas

app_name = 'api'
urlpatterns = [
    path('register/', register, name='register'),
    path('login/',  MyObtainAuthToken.as_view(), name='login'),
    path('users/<uuid:id>', users, name='users'),
    path('users/<uuid:user_id>/quotas/', quotas, name='quotas'),
]
