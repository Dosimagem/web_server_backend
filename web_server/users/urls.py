from django.urls import path
from django.contrib.auth import views as auth_views

from .views import index, profile, signup

#  TODO: app namespace
urlpatterns = [
    path('', index, name='index'),
    path('profile/', profile, name='profile'),
    path('accounts/signup/', signup, name='signup'),
    path('accounts/login/', auth_views.LoginView.as_view(template_name='users/login.html'), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(template_name='users/login.html'), name='logout'),
]
