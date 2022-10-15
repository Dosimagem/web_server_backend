from django.contrib import admin

from web_server.service.forms import CreateOrderForm
from web_server.service.models import (
    Calibration,
    ClinicDosimetryAnalysis,
    Isotope,
    Order,
    PreClinicDosimetryAnalysis,
    SegmentationAnalysis,
)


@admin.register(Order)
class UserOrderModelAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'code',
        'user',
        'quantity_of_analyzes',
        'remaining_of_analyzes',
        'price',
        'status_payment',
        'service_name',
        'permission',
    )

    list_display_links = (
        'code',
        'user',
    )
    readonly_fields = ('id', 'uuid', 'created_at', 'modified_at', 'code')
    search_fields = ('user__profile__clinic',)
    list_filter = ('user',)
    list_per_page = 20

    form = CreateOrderForm


@admin.register(Isotope)
class IstopeModelAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'created_at', 'modified_at')


@admin.register(Calibration)
class CalibrationModelAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'calibration_name',
        'user',
        'isotope',
        'syringe_activity',
        'residual_syringe_activity',
        'measurement_datetime',
        'phantom_volume',
        'acquisition_time',
        'images',
    )
    list_display_links = ('calibration_name',)
    readonly_fields = (
        'id',
        'uuid',
        'created_at',
        'modified_at',
    )
    search_fields = ('calibration_name',)
    list_filter = ('user',)
    list_per_page = 20


@admin.register(ClinicDosimetryAnalysis)
class ClinicDosimetryAnalysisAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'code',
        'analysis_name',
        'order',
        'calibration',
        'status',
        'injected_activity',
        'administration_datetime',
        'images',
        'report',
        'active',
    )
    list_display_links = (
        'code',
        'analysis_name',
    )
    readonly_fields = (
        'code',
        'id',
        'uuid',
        'created_at',
        'modified_at',
    )
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
    list_display = (
        'id',
        'code',
        'analysis_name',
        'order',
        'calibration',
        'status',
        'injected_activity',
        'administration_datetime',
        'images',
        'report',
        'active',
    )
    list_display_links = (
        'code',
        'analysis_name',
    )
    readonly_fields = (
        'code',
        'id',
        'uuid',
        'created_at',
        'modified_at',
    )
    search_fields = ('analysis_name',)
    list_per_page = 20
    list_filter = ('order__user', 'status', 'active', 'order')


@admin.register(SegmentationAnalysis)
class SegmentationAnalysisAdmin(admin.ModelAdmin):
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
    list_display_links = (
        'code',
        'analysis_name',
    )
    readonly_fields = (
        'code',
        'id',
        'uuid',
        'created_at',
        'modified_at',
    )
    search_fields = ('analysis_name',)
    list_per_page = 20
    list_filter = ('order__user', 'status', 'active', 'order')
