from django.urls import path

from .views import calulator_radiosynoviorthesis, isotopes

app_name = 'radiosyn'
urlpatterns = [
    path(
        'user/<uuid:user_id>/radiosynoviorthesis-calulator',
        calulator_radiosynoviorthesis,
        name='calculator',
    ),
    path('radiosynoviorthesis-calulator/isotopes/', isotopes, name='isotopes'),
]
