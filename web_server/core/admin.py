from django.contrib import admin

from .models import CostumUser


@admin.register(CostumUser)
class CostumUser(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone', 'institution', 'role', 'is_active', 'is_staff', 'date_joined')
