from django.contrib import admin
from .models import SalaryStructure, EmployeeSalaryStructure, SalarySlip, SalaryHistory


@admin.register(SalaryStructure)
class SalaryStructureAdmin(admin.ModelAdmin):
    list_display = ('name', 'basic_percentage', 'hra_percentage', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'description')
    ordering = ('-created_at',)


@admin.register(EmployeeSalaryStructure)
class EmployeeSalaryStructureAdmin(admin.ModelAdmin):
    list_display = ('employee', 'salary_structure', 'ctc', 'effective_from', 'is_active')
    list_filter = ('is_active', 'effective_from', 'salary_structure')
    search_fields = ('employee__full_name', 'employee__employee_code')
    ordering = ('-effective_from',)
    raw_id_fields = ('employee',)


@admin.register(SalarySlip)
class SalarySlipAdmin(admin.ModelAdmin):
    list_display = ('employee', 'month', 'year', 'gross_salary', 'net_salary', 'status')
    list_filter = ('status', 'year', 'month')
    search_fields = ('employee__full_name', 'employee__employee_code')
    ordering = ('-year', '-month')
    raw_id_fields = ('employee',)


@admin.register(SalaryHistory)
class SalaryHistoryAdmin(admin.ModelAdmin):
    list_display = ('employee', 'previous_ctc', 'new_ctc', 'increment_percentage', 'effective_date', 'reason')
    list_filter = ('effective_date', 'reason')
    search_fields = ('employee__full_name', 'employee__employee_code', 'reason')
    ordering = ('-effective_date',)
    raw_id_fields = ('employee',)
