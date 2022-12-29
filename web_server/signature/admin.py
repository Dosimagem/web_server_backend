from django.contrib import admin

from web_server.signature.models import Benefit, Signature


class BenefitInline(admin.StackedInline):
    model = Signature.benefits.through
    extra = 1
    verbose_name = 'Signature Benefit'


@admin.register(Benefit)
class BenefitModelAdmin(admin.ModelAdmin):

    fieldsets = (
        (
            'Benefit Data',
            {
                'fields': (
                    'name',
                    'uri',
                )
            },
        ),
        ('Other data', {'fields': ('id', 'uuid', 'created_at', 'modified_at')}),
    )

    list_display = ('name', 'uri')
    readonly_fields = ('id', 'uuid', 'created_at', 'modified_at')


@admin.register(Signature)
class SignatureModelAdmin(admin.ModelAdmin):

    inlines = [BenefitInline]

    fieldsets = (
        ('Data', {'fields': ('user', 'name', 'price', 'activated')}),
        ('Hired Period', {'fields': (('hired_period_initial', 'hired_period_end'),)}),
        ('Test Period', {'fields': (('test_period_initial', 'test_period_end'),)}),
        ('Other data', {'fields': ('id', 'uuid', 'created_at', 'modified_at')}),
    )

    list_display = (
        'user',
        'name',
        'price',
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
    list_filter = ('user', 'name')
    list_per_page = 20
