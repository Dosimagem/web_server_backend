from django.urls import path, include

from .views import index, profile, signup

#  TODO: app namespace
urlpatterns = [
    path('', index, name='index'),
    path('profile/', profile, name='profile'),
    path('accounts/signup/', signup, name='signup'),
    path('accounts/', include('django.contrib.auth.urls')),
]
