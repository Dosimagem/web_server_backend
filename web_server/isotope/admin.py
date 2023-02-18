from django.contrib import admin

from web_server.isotope.models import Isotope


@admin.register(Isotope)
class IstopeDosimetryModelAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'dosimetry', 'radiosyno', 'created_at', 'modified_at')
