from audioop import reverse
from django.contrib import admin
from django.utils.safestring import mark_safe

from web_server.service.models import Info, Order, Service


#@admin.register(Info)
class InfoInLine(admin.TabularInline):
    model = Info
    #list_display = ('camera_factor', 'radionuclide', 'injected_activity', 'injection_datetime', 'images')


@admin.register(Service)
class ServiceModelAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'unit_price', 'created_at', 'modified_at')
    list_display_links = ('name',)


@admin.register(Order)
class OrderModelAdmin(admin.ModelAdmin):
    list_display = ('requester', 'service', 'amount', 'status', 'total_price', 'info', 'report',)
    list_display_links = ('requester',)
    exclude = ('total_price',)

    # Add it to the details view:
    inlines =  (InfoInLine,)
