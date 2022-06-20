from django.contrib import admin

from web_server.service.models import Info, Order, Service


@admin.register(Service)
class ServiceModelAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'unit_price', 'created_at', 'modified_at')
    list_display_links = ('name',)


@admin.register(Order)
class OrderModelAdmin(admin.ModelAdmin):
    list_display = ('requester', 'service', 'amount', 'status', 'total_price', 'info')
    list_display_links = ('requester',)
    exclude = ('total_price',)


@admin.register(Info)
class InfoModelAdmin(admin.ModelAdmin):
    pass
