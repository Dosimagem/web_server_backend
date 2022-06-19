from django.contrib import admin

from .models import CostumUser


@admin.register(CostumUser)
class CostumUserModelAdmin(admin.ModelAdmin):
    list_display = ('email', 'name', 'phone', 'institution', 'role', 'is_active', 'is_staff', 'date_joined')
    list_display_links = ('email',)
