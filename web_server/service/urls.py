from django.urls import path

from .views.analysis import analysis_list_create, analysis_read_update_delete
from .views.calibrations import (
    calibrations_list_create,
    calibrations_read_update_delete,
)
from .views.isotopes import isotope
from .views.orders import orders_list, orders_read

app_name = 'service'
urlpatterns = [
    #
    path('users/<uuid:user_id>/orders/', orders_list, name='order-list'),
    path('users/<uuid:user_id>/orders/<uuid:order_id>', orders_read, name='order-read'),
    #
    path('isotopes/', isotope, name='isotopes-list'),
    #
    path('users/<uuid:user_id>/calibrations/', calibrations_list_create, name='calibration-list-create'),
    path(
        'users/<uuid:user_id>/calibrations/<uuid:calibration_id>',
        calibrations_read_update_delete,
        name='calibration-read-update-delete',
    ),
    #
    path('users/<uuid:user_id>/orders/<uuid:order_id>/analysis/', analysis_list_create, name='analysis-list-create'),
    path(
        'users/<uuid:user_id>/orders/<uuid:order_id>/analysis/<uuid:analysis_id>',
        analysis_read_update_delete,
        name='analysis-read-update-delete',
    ),
]
