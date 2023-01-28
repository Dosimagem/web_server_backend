from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from web_server.service.forms import CreateOrderForm
from web_server.service.models import (
    Calibration,
    ClinicDosimetryAnalysis,
    Isotope,
    Order,
    PreClinicDosimetryAnalysis,
    RadiosynoAnalysis,
    SegmentationAnalysis,
)


@admin.register(Order)
class OrderModelAdmin(admin.ModelAdmin):

    fieldsets = (
        (
            _('Main data'),
            {
                'fields': (
                    'service_name',
                    'quantity_of_analyzes',
                    'price',
                    'status_payment',
                    'user',
                    'active',
                )
            },
        ),
        (
            _('Other data'),
            {
                'classes': ('collapse',),
                'fields': (
                    'remaining_of_analyzes',
                    'id',
                    'uuid',
                    'created_at',
                    'modified_at',
                ),
            },
        ),
    )

    list_display = (
        'id',
        'code',
        'user',
        'quantity_of_analyzes',
        'remaining_of_analyzes',
        'price',
        'status_payment',
        'service_name',
        'active',
    )

    list_display_links = (
        'code',
        'user',
    )
    readonly_fields = (
        'id',
        'uuid',
        'created_at',
        'modified_at',
        'code',
    )
    search_fields = ('user__profile__clinic',)
    list_filter = ('user', 'service_name', 'status_payment')
    list_per_page = 20

    form = CreateOrderForm


@admin.register(Isotope)
class IstopeModelAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'created_at', 'modified_at')


@admin.register(Calibration)
class CalibrationModelAdmin(admin.ModelAdmin):

    fieldsets = (
        (
            _('Calibration data'),
            {
                'fields': (
                    'calibration_name',
                    'isotope',
                    'syringe_activity',
                    'residual_syringe_activity',
                    'measurement_datetime',
                    'phantom_volume',
                    'acquisition_time',
                    'user',
                )
            },
        ),
        (_('Files'), {'fields': ('images',)}),
        (_('Other data'), {'classes': ('collapse',), 'fields': ('id', 'uuid')}),
    )

    list_display = ('id', 'calibration_name', 'user', 'isotope', 'images')
    list_display_links = ('calibration_name',)
    readonly_fields = ('id', 'uuid', 'created_at', 'modified_at')
    search_fields = ('calibration_name',)
    list_filter = ('user',)
    list_per_page = 20


@admin.register(ClinicDosimetryAnalysis)
class ClinicDosimetryAnalysisAdmin(admin.ModelAdmin):

    fieldsets = (
        (
            _('Analysis data'),
            {
                'fields': (
                    'analysis_name',
                    'injected_activity',
                    'administration_datetime',
                    'status',
                    'active',
                )
            },
        ),
        (_('Files'), {'fields': ('report', 'images')}),
        (_('Order & Calibration'), {'fields': ('order', 'calibration')}),
        (_('Feedback'), {'classes': ('collapse',), 'fields': ('message_to_user',)}),
        (_('Other data'), {'classes': ('collapse',), 'fields': ('id', 'uuid', 'created_at', 'modified_at')}),
    )

    list_display = (
        'id',
        'code',
        'analysis_name',
        'order',
        'calibration',
        'status',
        'images',
        'report',
        'active',
    )
    list_display_links = ('code', 'analysis_name')
    readonly_fields = ('code', 'id', 'uuid', 'order', 'calibration', 'created_at', 'modified_at')
    search_fields = ('analysis_name',)
    list_per_page = 20
    list_filter = ('order__user', 'status', 'active', 'order')

    # def formfield_for_foreignkey(self, db_field, request, **kwargs):
    #     if db_field.name == 'order':
    #         kwargs["queryset"] = Order.objects.filter(code__endswith=self.model.CODE)
    #     # if db_field.name == 'calibration':
    #     #     kwargs["queryset"] = Calibration.objects.filter(user=self.model.order.user)
    #     return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(PreClinicDosimetryAnalysis)
class PreClinicDosimetryAnalysisAdmin(admin.ModelAdmin):

    fieldsets = (
        (
            _('Analysis data'),
            {
                'fields': (
                    'analysis_name',
                    'injected_activity',
                    'administration_datetime',
                    'status',
                    'active',
                )
            },
        ),
        (_('Files'), {'fields': ('report', 'images')}),
        (_('Order & Calibration'), {'fields': ('order', 'calibration')}),
        (_('Feedback'), {'classes': ('collapse',), 'fields': ('message_to_user',)}),
        (_('Other data'), {'classes': ('collapse',), 'fields': ('uuid', 'created_at', 'modified_at')}),
    )

    list_display = (
        'id',
        'code',
        'analysis_name',
        'order',
        'calibration',
        'status',
        'images',
        'report',
        'active',
    )
    list_display_links = ('code', 'analysis_name')
    readonly_fields = ('code', 'id', 'uuid', 'order', 'calibration', 'created_at', 'modified_at')
    search_fields = ('analysis_name',)
    list_per_page = 20
    list_filter = ('order__user', 'status', 'active', 'order')


@admin.register(SegmentationAnalysis)
class SegmentationAnalysisAdmin(admin.ModelAdmin):

    fieldsets = (
        (_('Analysis data'), {'fields': ('analysis_name', 'status', 'active')}),
        (_('Files'), {'fields': ('report', 'images')}),
        (_('Order'), {'fields': ('order',)}),
        (_('Feeback'), {'classes': ('collapse',), 'fields': ('message_to_user',)}),
        (_('Other data'), {'classes': ('collapse',), 'fields': ('id', 'uuid', 'created_at', 'modified_at')}),
    )

    list_display = (
        'id',
        'code',
        'analysis_name',
        'order',
        'status',
        'images',
        'report',
        'active',
    )
    list_display_links = ('code', 'analysis_name')
    readonly_fields = (
        'code',
        'id',
        'uuid',
        'order',
        'created_at',
        'modified_at',
    )
    search_fields = ('analysis_name',)
    list_per_page = 20
    list_filter = ('order__user', 'status', 'active', 'order')


@admin.register(RadiosynoAnalysis)
class RadiosynoviorthesisAdmin(admin.ModelAdmin):

    fieldsets = (
        (_('Analysis data'), {'fields': ('analysis_name', 'isotope', 'status')}),
        (_('Files'), {'fields': ('report', 'images')}),
        (_('Order'), {'fields': ('order',)}),
        (_('Feeback'), {'classes': ('collapse',), 'fields': ('message_to_user',)}),
        (_('Other data'), {'fields': ('id', 'uuid', 'active', 'created_at', 'modified_at')}),
    )

    list_display = (
        'id',
        'code',
        'analysis_name',
        'order',
        'status',
        'isotope',
        'images',
        'report',
        'active',
    )
    list_display_links = ('code', 'analysis_name')
    readonly_fields = ('code', 'id', 'order', 'uuid', 'created_at', 'modified_at')
    search_fields = ('analysis_name',)
    list_per_page = 20
    list_filter = ('order__user', 'status', 'active', 'order')
