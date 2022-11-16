from django.contrib import admin

from web_server.notification.models import Notification

# Register your models here.


@admin.register(Notification)
class NotificationModelAdmin(admin.ModelAdmin):

    fieldsets = (
        (
            'Notification data',
            {
                'fields': (
                    'user',
                    'message',
                    'kind',
                    'checked',
                )
            },
        ),
        (
            'Other data',
            {
                'fields': (
                    'id',
                    'uuid',
                    'created_at',
                    'modified_at',
                )
            },
        ),
    )

    list_display = (
        'uuid',
        'user',
        'message',
        'checked',
        'kind',
    )

    list_display_links = ('uuid',)

    readonly_fields = (
        'id',
        'uuid',
        'created_at',
        'modified_at',
    )
    search_fields = ('message',)
    list_filter = ('user', 'kind', 'checked')
    list_per_page = 20
