from django.urls import path
from . import views

app_name = 'salary'

urlpatterns = [
    # Salary Structure
    path('structures/', views.salary_structure_list, name='structure_list'),
    path('structures/create/', views.salary_structure_create, name='structure_create'),
    path('structures/<int:pk>/edit/', views.salary_structure_edit, name='structure_edit'),
    path('structures/<int:pk>/delete/', views.salary_structure_delete, name='structure_delete'),
    
    # CTC Calculator
    path('calculator/', views.ctc_calculator, name='ctc_calculator'),
    path('calculator/ajax/', views.calculate_ctc_ajax, name='calculate_ctc_ajax'),
    
    # Employee Salary Assignment
    path('assignments/', views.employee_salary_list, name='employee_salary_list'),
    path('assignments/assign/', views.employee_salary_assign, name='employee_salary_assign'),
    path('assignments/<int:pk>/edit/', views.employee_salary_edit, name='employee_salary_edit'),
    
    # Salary Slips
    path('slips/', views.salary_slip_list, name='slip_list'),
    path('slips/generate/', views.salary_slip_generate, name='slip_generate'),
    path('slips/<int:pk>/', views.salary_slip_detail, name='slip_detail'),
    path('slips/<int:pk>/pdf/', views.salary_slip_pdf, name='slip_pdf'),
    
    # Salary History
    path('history/', views.salary_history_list, name='history_list'),
    path('history/<int:employee_id>/', views.salary_history_list, name='employee_history'),
]
