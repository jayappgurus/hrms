from django.contrib import admin
from django.contrib.auth.models import Group, User
from django.contrib.auth.admin import UserAdmin as DefaultUserAdmin
from django.utils.html import format_html
from .models import Department, Designation, EmergencyContact, Employee, EmployeeDocument, UserProfile, PublicHoliday, Notification, Message
from .decorators import role_required

# Use the default admin site but customize it
admin.site.site_header = "HRMS Portal"
admin.site.site_title = "HRMS Portal Administration"
admin.site.index_title = "Welcome to HRMS Portal Administration"

# Temporarily use default UserAdmin to avoid Python 3.14 compatibility issues
# Custom User Admin code commented out for now
"""
# Unregister the default UserAdmin and register our custom one
admin.site.unregister(User)

# Custom User Admin to avoid template context issues
@admin.register(User)
class CustomUserAdmin(DefaultUserAdmin):
    list_display = ['username', 'email', 'first_name', 'last_name', 'user_role', 'is_staff', 'is_active']
    list_filter = ['is_staff', 'is_superuser', 'is_active', 'date_joined', 'profile__role']
    search_fields = ['username', 'first_name', 'last_name', 'email']

    # Define fieldsets directly to avoid super() calls
    fieldsets = (
        (None, {
            'fields': ('username', 'password')
        }),
        ('Personal info', {
            'fields': ('first_name', 'last_name', 'email')
        }),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        ('Important dates', {
            'fields': ('last_login', 'date_joined'),
        }),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2'),
        }),
    )

    def user_role(self, obj):
        try:
            profile = obj.profile
            color = {
                'admin': 'red',
                'hr': 'blue',
                'manager': 'green',
                'it_admin': 'orange',
                'employee': 'gray'
            }.get(profile.role, 'gray')
            return format_html(
                '<span style="color: {}; font-weight: bold;">{}</span>',
                color,
                profile.get_role_display()
            )
        except UserProfile.DoesNotExist:
            return format_html(
                '<span style="color: gray; font-style: italic;">No Profile</span>'
            )
    user_role.short_description = 'Role'
    user_role.admin_order_field = 'profile__role'
"""

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'role', 'department', 'phone', 'created_at']
    list_filter = ['role', 'department', 'created_at']
    search_fields = ['user__username', 'user__first_name', 'user__last_name', 'user__email']
    ordering = ['-created_at']

    fieldsets = (
        (None, {
            'fields': ('user', 'role', 'department', 'phone', 'address')
        }),
        ('System Information', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ['created_at', 'updated_at']


    def changelist_view(self, request, extra_context=None):
        return super().changelist_view(request, extra_context=extra_context)

@admin.register(Department)
class SimpleDepartmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'created_at']
    search_fields = ['name', 'description']
    list_filter = ['created_at']
    ordering = ['name']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Designation)
class DesignationAdmin(admin.ModelAdmin):
    list_display = ['name', 'department', 'description', 'created_at', 'updated_at']
    list_filter = ['department', 'created_at']
    search_fields = ['name', 'department__name', 'description']
    ordering = ['department', 'name']

    fieldsets = (
        (None, {
            'fields': ('name', 'department', 'description')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ['created_at', 'updated_at']


@admin.register(EmergencyContact)
class EmergencyContactAdmin(admin.ModelAdmin):
    list_display = ['name', 'relationship', 'mobile_number', 'email']
    search_fields = ['name', 'relationship', 'mobile_number', 'email']
    ordering = ['name']

class EmployeeDocumentInline(admin.TabularInline):
    model = EmployeeDocument
    extra = 0
    fields = ['document_type', 'is_submitted', 'submitted_date', 'remarks']
    readonly_fields = ['submitted_date']

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ['employee_code', 'full_name', 'department', 'designation',
                   'employment_status_badge', 'period_type_badge', 'joining_date', 'mobile_number']
    list_filter = ['department', 'designation', 'employment_status', 'period_type', 'joining_date']
    search_fields = ['employee_code', 'full_name', 'mobile_number', 'official_email']
    ordering = ['-created_at']
    inlines = [EmployeeDocumentInline]
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        ('Core Employee Details', {
            'fields': ('employee_code', 'full_name', 'department', 'designation',
                      'joining_date', 'relieving_date', 'employment_status')
        }),
        ('Contact Information', {
            'fields': ('mobile_number', 'official_email', 'personal_email',
                      'local_address', 'permanent_address')
        }),
        ('Emergency Contact', {
            'fields': ('emergency_contact',)
        }),
        ('Personal Information', {
            'fields': ('date_of_birth', 'marital_status', 'anniversary_date')
        }),
        ('Professional Information', {
            'fields': ('highest_qualification', 'total_experience_years',
                      'total_experience_months', 'period_type')
        }),
        ('Identity & Compliance', {
            'fields': ('aadhar_card_number', 'pan_card_number')
        }),
        ('System Information', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def employment_status_badge(self, obj):
        color = 'green' if obj.employment_status == 'active' else 'red'
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_employment_status_display()
        )
    employment_status_badge.short_description = 'Status'
    employment_status_badge.admin_order_field = 'employment_status'

    def period_type_badge(self, obj):
        color_map = {
            'trainee': 'purple',
            'intern': 'teal',
            'probation': 'orange',
            'notice_period': 'red',
            'confirmed': 'green'
        }
        color = color_map.get(obj.period_type, 'gray')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_period_type_display()
        )
    period_type_badge.short_description = 'Period Type'
    period_type_badge.admin_order_field = 'period_type'


@admin.register(EmployeeDocument)
class EmployeeDocumentAdmin(admin.ModelAdmin):
    list_display = ['employee', 'document_type', 'is_submitted_badge', 'submitted_date', 'created_at']
    list_filter = ['document_type', 'is_submitted', 'submitted_date', 'created_at']
    search_fields = ['employee__full_name', 'employee__employee_code', 'document_type']
    ordering = ['-created_at']

    fieldsets = (
        (None, {
            'fields': ('employee', 'document_type', 'is_submitted', 'submitted_date')
        }),
        ('Additional Information', {
            'fields': ('document_file', 'remarks')
        }),
        ('System Information', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ['created_at', 'updated_at']

    def is_submitted_badge(self, obj):
        color = 'green' if obj.is_submitted else 'gray'
        text = 'Submitted' if obj.is_submitted else 'Pending'
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            text
        )
    is_submitted_badge.short_description = 'Status'
    is_submitted_badge.admin_order_field = 'is_submitted'


# Hide Group model from admin
try:
    admin.site.unregister(Group)
except admin.sites.NotRegistered:
    pass

# Public Holiday Admin
@admin.register(PublicHoliday)
class PublicHolidayAdmin(admin.ModelAdmin):
    list_display = ('name', 'date', 'day', 'year', 'is_active')
    list_filter = ('year', 'is_active', 'day')
    search_fields = ('name', 'date')
    list_editable = ('is_active',)
    ordering = ('date',)

    fieldsets = (
        ('Holiday Information', {
            'fields': ('name', 'date', 'day', 'year')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
    )

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('title', 'notification_type', 'created_by', 'created_at', 'is_active', 'target_all')
    list_filter = ('notification_type', 'is_active', 'target_all', 'created_at')
    search_fields = ('title', 'message')
    filter_horizontal = ('target_users',)
    readonly_fields = ('created_at',)

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('subject', 'sender', 'created_at', 'target_all')
    list_filter = ('target_all', 'created_at')
    search_fields = ('subject', 'body')
    filter_horizontal = ('target_users',)
    readonly_fields = ('created_at',)
