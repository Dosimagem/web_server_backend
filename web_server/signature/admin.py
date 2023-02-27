from django.contrib import admin
from django.utils.translation import gettext as _

from web_server.signature.models import Benefit, Signature


class BenefitInline(admin.StackedInline):
    model = Signature.benefits.through
    extra = 1
    verbose_name = _('Benefits')


@admin.register(Benefit)
class BenefitModelAdmin(admin.ModelAdmin):

    fieldsets = (
        (
            _('Main data'),
            {
                'fields': (
                    'name',
                    'uri',
                )
            },
        ),
        (
            _('Other data'),
            {
                'classes': ('collapse',),
                'fields': ('id', 'uuid', 'created_at', 'modified_at'),
            },
        ),
    )

    list_display = ('name', 'uri')
    readonly_fields = ('id', 'uuid', 'created_at', 'modified_at')


@admin.register(Signature)
class SignatureModelAdmin(admin.ModelAdmin):

    inlines = [BenefitInline]

    fieldsets = (
        (
            _('Main data'),
            {
                'fields': (
                    'user',
                    'plan',
                    'price',
                    'discount',
                    'modality',
                    'status_payment',
                    'bill',
                    'activated',
                )
            },
        ),
        (
            _('Hired Period'),
            {
                'classes': ('collapse',),
                'fields': (('hired_period_initial', 'hired_period_end'),),
            },
        ),
        (
            _('Test Period'),
            {
                'classes': ('collapse',),
                'fields': (('test_period_initial', 'test_period_end'),),
            },
        ),
        (
            _('Other data'),
            {
                'classes': ('collapse',),
                'fields': ('id', 'uuid', 'created_at', 'modified_at'),
            },
        ),
    )

    list_display = (
        'id',
        'plan',
        'user',
        'price',
        'discount',
        'modality',
        'hired_period_initial',
        'hired_period_end',
        'test_period_initial',
        'test_period_end',
        'activated',
    )

    readonly_fields = (
        'id',
        'uuid',
        'created_at',
        'modified_at',
    )

    search_fields = ('user__profile__clinic',)
    list_display_links = ('id', 'plan', 'user')
    list_filter = ('user', 'plan')
    list_per_page = 20
