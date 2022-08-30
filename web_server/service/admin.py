
from django.contrib import admin


from web_server.service.models import UserQuota


@admin.register(UserQuota)
class UserQuotasModelAdmin(admin.ModelAdmin):
    list_display = (
                   'id',
                   'uuid',
                   'user',
                   'amount',
                   'price',
                   'service_type',
                   'status_payment',
                   'created_at',
                   'modified_at'
                   )

    list_display_links = ('user',)
