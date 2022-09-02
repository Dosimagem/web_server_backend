from django.urls import path

from .views.register import register, MyObtainAuthToken
from .views.users import users
from .views.orders import orders_list, orders_read


app_name = 'api'
urlpatterns = [
    path('register/', register, name='register'),
    path('login/',  MyObtainAuthToken.as_view(), name='login'),
    path('users/<uuid:id>/', users, name='users'),
    path('users/<uuid:user_id>/orders/', orders_list, name='order-list'),
    path('users/<uuid:user_id>/orders/<uuid:order_id>/', orders_read, name='order-read'),
]
