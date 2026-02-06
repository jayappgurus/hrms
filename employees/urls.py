from django.urls import path
from . import views
from . import views_user_management

app_name = 'employees'

urlpatterns = [
    path('', views.DashboardView.as_view(), name='dashboard'),
    path('employees/', views.EmployeeListView.as_view(), name='employee_list'),
    path('employee/<int:pk>/', views.EmployeeDetailView.as_view(), name='employee_detail'),
    path('employee/add/', views.EmployeeCreateView.as_view(), name='employee_add'),
    path('employee/<int:pk>/edit/', views.EmployeeUpdateView.as_view(), name='employee_edit'),
    path('employee/<int:pk>/toggle-status/', views.toggle_employee_status, name='toggle_employee_status'),
    path('employee/<int:employee_pk>/document/<str:document_type>/update/', 
         views.update_document_status, name='update_document_status'),
    path('ajax/get-designations/', views.get_designations_by_department, name='get_designations_by_department'),
    
    # User Management URLs
    path('users/', views_user_management.UserListView.as_view(), name='user_list'),
    path('users/<int:pk>/profile/', views_user_management.UserProfileUpdateView.as_view(), name='edit_user_profile'),
    path('users/<int:user_id>/create-profile/', views_user_management.create_user_profile, name='create_user_profile'),
    path('users/<int:user_id>/assign-role/', views_user_management.assign_role, name='assign_role'),
    path('my-profile/', views_user_management.my_profile, name='my_profile'),
]
