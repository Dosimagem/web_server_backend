from django.urls import path, include

from .views import index, signup

app_name = 'core'
urlpatterns = [
    path('', index, name='index'),
    path('accounts/signup/', signup, name='signup'),
    path('accounts/', include('django.contrib.auth.urls')),
]
