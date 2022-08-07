from django.contrib import admin

from .models import CustomUser, UserProfile


@admin.register(CustomUser)
class CustomUserModelAdmin(admin.ModelAdmin):
    list_display = ('id', 'email', 'is_active', 'is_staff', 'date_joined')
    list_display_links = ('email',)


@admin.register(UserProfile)
class UserProfileModelAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'phone', 'institution', 'role', 'user')
    list_display_links = ('id', 'name',)
