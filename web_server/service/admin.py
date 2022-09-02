
from django.contrib import admin
from web_server.service.forms import CreateOrderForm


from web_server.service.models import Order


@admin.register(Order)
class UserOrderModelAdmin(admin.ModelAdmin):
    list_display = (
                   'uuid',
                   'id',
                   'user',
                   'quantity_of_analyzes',
                   'remaining_of_analyzes',
                   'price',
                   'status_payment',
                   'service_name',
                   'permission',
                   'created_at',
                   'modified_at'
                   )

    list_display_links = ('uuid',)

    form = CreateOrderForm
