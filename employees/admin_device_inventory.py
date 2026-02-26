from django.contrib import admin
from .models import CPUDevice, ScreenDevice, KeyboardDevice, MouseDevice, HeadphoneDevice, ExtenderDevice


@admin.register(CPUDevice)
class CPUDeviceAdmin(admin.ModelAdmin):
    list_display = ['company_name', 'processor', 'ram', 'storage', 'label_no', 'status', 'allocated_to', 'created_at']
    list_filter = ['status', 'company_name', 'created_at']
    search_fields = ['company_name', 'label_no', 'processor', 'allocated_to__full_name']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('company_name', 'processor', 'ram', 'storage', 'label_no', 'mac_address')
        }),
        ('Allocation', {
            'fields': ('status', 'allocated_to', 'allocated_date')
        }),
        ('Additional Info', {
            'fields': ('notes',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )


@admin.register(ScreenDevice)
class ScreenDeviceAdmin(admin.ModelAdmin):
    list_display = ['company_name', 'size', 'label_no', 'status', 'allocated_to', 'created_at']
    list_filter = ['status', 'company_name', 'created_at']
    search_fields = ['company_name', 'label_no', 'allocated_to__full_name']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(KeyboardDevice)
class KeyboardDeviceAdmin(admin.ModelAdmin):
    list_display = ['company_name', 'label_no', 'status', 'allocated_to', 'created_at']
    list_filter = ['status', 'company_name', 'created_at']
    search_fields = ['company_name', 'label_no', 'allocated_to__full_name']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(MouseDevice)
class MouseDeviceAdmin(admin.ModelAdmin):
    list_display = ['company_name', 'label_no', 'status', 'allocated_to', 'created_at']
    list_filter = ['status', 'company_name', 'created_at']
    search_fields = ['company_name', 'label_no', 'allocated_to__full_name']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(HeadphoneDevice)
class HeadphoneDeviceAdmin(admin.ModelAdmin):
    list_display = ['company_name', 'label_no', 'status', 'allocated_to', 'created_at']
    list_filter = ['status', 'company_name', 'created_at']
    search_fields = ['company_name', 'label_no', 'allocated_to__full_name']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(ExtenderDevice)
class ExtenderDeviceAdmin(admin.ModelAdmin):
    list_display = ['company_name', 'model', 'label_no', 'status', 'allocated_to', 'created_at']
    list_filter = ['status', 'company_name', 'created_at']
    search_fields = ['company_name', 'label_no', 'model', 'allocated_to__full_name']
    readonly_fields = ['created_at', 'updated_at']
