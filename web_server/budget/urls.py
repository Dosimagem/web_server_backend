from django.urls import path

from .views import general_budget_mail

app_name = 'budget'
urlpatterns = [
    path('users/<uuid:user_id>/budget/', general_budget_mail, name='general-budget'),
]
