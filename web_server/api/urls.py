from django.urls import path

from .views.register import register, MyObtainAuthToken
from .views.users import users
from .views.orders import orders_list_create, orders_read_patch_delete


app_name = 'api'
urlpatterns = [
    path('register/', register, name='register'),
    path('login/',  MyObtainAuthToken.as_view(), name='login'),
    path('users/<uuid:id>/', users, name='users'),
    path('users/<uuid:user_id>/orders/', orders_list_create, name='create-list'),
    path('users/<uuid:user_id>/orders/<uuid:order_id>/', orders_read_patch_delete, name='read-patch-delete'),
]
