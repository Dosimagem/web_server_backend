from django.contrib import admin

from web_server.service.models import Service


@admin.register(Service)
class ServeceModelAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'unit_price', 'created_at', 'modified_at')
    list_display_links = ('name',)
