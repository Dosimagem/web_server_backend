from django.urls import path

from .views import comp_model_budget_mail, general_budget_mail

app_name = 'budget'
urlpatterns = [
    path('users/<uuid:user_id>/budget/general/', general_budget_mail, name='general-budget'),
    path('users/<uuid:user_id>/budget/comp_modelling/', comp_model_budget_mail, name='comp-modelling-budget'),
]
