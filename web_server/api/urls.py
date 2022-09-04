from django.urls import path

from .views.register import register, MyObtainAuthToken
from .views.users import users
from .views.orders import orders_list, orders_read
from .views.isotopes import isotope
from .views.calibrations import calibrations_list_create, calibrations_read_update_delete


app_name = 'api'
urlpatterns = [
    path('register/', register, name='register'),
    path('login/',  MyObtainAuthToken.as_view(), name='login'),
    #
    path('users/<uuid:id>', users, name='users'),
    path('users/<uuid:user_id>/orders/', orders_list, name='order-list'),
    path('users/<uuid:user_id>/orders/<uuid:order_id>', orders_read, name='order-read'),
    #
    path('isotopes/', isotope, name='isotopes-list'),
    #
    path('users/<uuid:user_id>/calibrations/', calibrations_list_create, name='calibration-list-create'),
    path('users/<uuid:user_id>/calibrations/<uuid:calibration_id>', calibrations_read_update_delete,
         name='calibration-read-update-delete')
]
