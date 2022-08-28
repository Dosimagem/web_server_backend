
# from django.contrib import admin

# from web_server.service.models import (ComputationalModelOrder,
#                                        DosimetryOrder,
#                                        SegmentationOrder,
#                                        Service)


# @admin.register(Service)
# class ServiceModelAdmin(admin.ModelAdmin):
#     list_display = ('id', 'name', 'description', 'unit_price', 'created_at', 'modified_at')
#     list_display_links = ('name',)


# @admin.register(DosimetryOrder)
# class DosimetryOrderModelAdmin(admin.ModelAdmin):
#     list_display = ('id', 'requester', 'service', 'amount', 'status', 'total_price', 'report', 'images', 'created_at')
#     list_display_links = ('requester',)
#     exclude = ('total_price', 'type')


# @admin.register(ComputationalModelOrder)
# class ComputationalModelOrderModelAdmin(admin.ModelAdmin):
#     list_display = ('id', 'requester', 'service', 'amount', 'status', 'total_price', 'report', 'images', 'created_at')
#     list_display_links = ('requester',)
#     exclude = ('total_price',)


# @admin.register(SegmentationOrder)
# class SegmentationOrderModelAdmin(admin.ModelAdmin):
#     list_display = ('id', 'requester', 'service', 'amount', 'status', 'total_price', 'report', 'images', 'created_at')
#     list_display_links = ('requester',)
#     exclude = ('total_price',)
