from django.contrib import admin

from web_server.service.forms import CreateOrderForm
from web_server.service.models import Calibration, ClinicDosimetryAnalysis, Isotope, Order, PreClinicDosimetryAnalysis


@admin.register(Order)
class UserOrderModelAdmin(admin.ModelAdmin):
    list_display = (
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


@admin.register(PreClinicDosimetryAnalysis)
class PreClinicDosimetryAnalysisAdmin(admin.ModelAdmin):
    list_display = (
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
