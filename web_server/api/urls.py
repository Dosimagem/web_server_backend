from django.urls import path

from .views.register import register, MyObtainAuthToken
from .views.users import users
from .views.quotas import quotas_list_create, quotas_read_patch_delete


app_name = 'api'
urlpatterns = [
    path('register/', register, name='register'),
    path('login/',  MyObtainAuthToken.as_view(), name='login'),
    path('users/<uuid:id>/', users, name='users'),
    path('users/<uuid:user_id>/quotas/', quotas_list_create, name='create-list'),
    path('users/<uuid:user_id>/quotas/<uuid:quota_id>/', quotas_read_patch_delete, name='read-patch-delete'),
]
