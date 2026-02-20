from django.urls import path
from . import views_job
from . import views_user_management
from . import views_department
from . import views
from . import views_auth
from . import views_job_application as views_job_app
from . import views_csv
from . import views_notifications
from . import views_salary
from . import views_system
from . import views_performance
from . import views_api
from . import views_assignment
from . import views_account_management
from . import views_system_management
app_name = 'employees'
urlpatterns = [
     
    # Performance Evaluation
    path('performance/evaluations/', views_performance.EvaluationDashboardView.as_view(), name='evaluation_dashboard'),
    path('performance/trainee-intern-evaluations/', views_performance.TraineeInternEvaluationDashboardView.as_view(), name='trainee_intern_evaluation_dashboard'),
    path('performance/probation-evaluations/', views_performance.ProbationEvaluationDashboardView.as_view(), name='probation_evaluation_dashboard'),
    path('performance/evaluation/<int:pk>/', views_performance.EvaluationDetailView.as_view(), name='evaluation_detail'),
    path('performance/evaluation/<int:pk>/submit/', views_performance.submit_evaluation, name='submit_evaluation'),
    path('performance/evaluation/<int:pk>/approve/', views_performance.approve_evaluation, name='approve_evaluation'),
    path('performance/evaluation/<int:pk>/reject/', views_performance.reject_evaluation, name='reject_evaluation'),
    path('performance/evaluation/<int:pk>/assign-manager/', views_assignment.assign_manager, name='evaluation_assign_manager'),

    # Salary & Increment Details
    path('employee/<int:pk>/salary/', views_salary.SalaryDetailsView.as_view(), name='salary_details'),
    path('employee/<int:pk>/increments/', views_salary.IncrementDetailsView.as_view(), name='increment_details'),
    path('employee/<int:pk>/payslip/generate/', views_salary.GeneratePaySlipView.as_view(), name='generate_payslip'),
    path('payslip/download/<int:slip_id>/', views_salary.download_payslip, name='download_payslip'),

    # Registration
    path('register/', views_auth.EmployeeRegistrationView.as_view(), name='register'),

    # Dashboard and API
    path('', views.DashboardView.as_view(), name='dashboard'),
    path('api/calendar-events/', views.CalendarEventsView.as_view(), name='calendar_events'),

    # Department & Designation Management
    path('departments/', views_department.department_management, name='department_management'),
    path('departments/add/', views_department.add_department, name='add_department'),
    path('designations/add/', views_department.add_designation, name='add_designation'),
    path('ajax/get-designations/', views.get_designations_by_department, name='get_designations_by_department'),
    path('api/designations/', views.DesignationAPIView.as_view(), name='designations_api'),

    # Employee Management

    path('employees/', views.EmployeeListView.as_view(), name='employee_list'),
    path('employees/add/', views.EmployeeCreateView.as_view(), name='employee_add'),
    path('employee/<int:pk>/', views.EmployeeDetailView.as_view(), name='employee_detail'),
    path('employee/<int:pk>/edit/', views.EmployeeUpdateView.as_view(), name='employee_edit'),
    path('employee/<int:pk>/delete/', views.EmployeeDeleteView.as_view(), name='employee_delete_record'),
    path('employee/<int:pk>/toggle-status/', views.toggle_employee_status, name='toggle_employee_status'),
    path('employee/<int:employee_pk>/document/<str:document_type>/update/',
         views.update_document_status, name='update_document_status'),
    path('update-document-status/<int:document_id>/',
         views.update_document_status_by_id, name='update_document_status_by_id'),

    # Employee CSV Import/Export
    path('employees/export-csv/', views_csv.export_employees_csv, name='export_employees_csv'),
    path('employees/import-csv/', views_csv.import_employees_csv, name='import_employees_csv'),
    path('employees/sample-csv/', views_csv.download_employee_sample_csv, name='download_employee_sample_csv'),

    # Device Management
    path('devices/', views.DeviceListView.as_view(), name='device_list'),
    path('devices/add/', views.DeviceCreateView.as_view(), name='device_add'),
    path('devices/<int:pk>/edit/', views.DeviceUpdateView.as_view(), name='device_edit'),
    path('devices/<int:pk>/delete/', views.DeviceDeleteView.as_view(), name='device_delete'),
    path('devices/visibility/', views.DeviceVisibilityView.as_view(), name='device_visibility'),
    path('devices/<int:pk>/allocate/', views.allocate_device, name='allocate_device'),
    path('devices/<int:pk>/return/', views.return_device, name='return_device'),

    # Device Request Management
    path('device-request/add/', views.DeviceRequestCreateView.as_view(), name='device_request_add'),
    path('asset-management/', views.asset_management, name='asset_management'),
    path('device-request/<int:request_id>/details/', views.device_request_details, name='device_request_details'),
    path('device-request/<int:request_id>/approve/', views.approve_device_request, name='approve_device_request'),
    path('device-request/<int:request_id>/reject/', views.reject_device_request, name='reject_device_request'),
    path('device-request/<int:request_id>/available-devices/', views.get_available_devices, name='get_available_devices'),
    path('device-request/<int:request_id>/allocate/', views.allocate_device_to_request, name='allocate_device_to_request'),
    path('device-request/<int:request_id>/request-return/', views.request_device_return, name='request_device_return'),
    path('device-request/<int:request_id>/approve-return/', views.approve_device_return, name='approve_device_return'),

    # API Endpoints
    path('api/available-devices/<str:device_type>/', views_api.api_available_devices, name='api_available_devices'),
    path('api/employees/', views_api.api_employees_list, name='api_employees_list'),
    path('api/employees/<int:employee_id>/', views_api.api_employee_detail, name='api_employee_detail'),
    path('api/departments/', views_api.api_departments, name='api_departments'),
    path('api/designations/', views_api.api_designations, name='api_designations'),
    path('api/employees/stats/', views_api.api_employee_stats, name='api_employee_stats'),

    # Leave & Holiday Management

    path('holidays/', views.PublicHolidayListView.as_view(), name='public_holidays'),
    path('holidays/add/', views.PublicHolidayCreateView.as_view(), name='public_holiday_add'),
    path('holidays/bulk-delete/', views.bulk_delete_public_holidays, name='bulk_delete_public_holidays'),
    path('holidays/<str:country>/', views.PublicHolidayListView.as_view(), name='public_holidays_by_country'),
    path('holidays/<int:pk>/edit/', views.PublicHolidayUpdateView.as_view(), name='public_holiday_edit'),
    path('holidays/<int:pk>/delete/', views.PublicHolidayDeleteView.as_view(), name='public_holiday_delete'),

    # Public Holiday CSV Import/Export
    path('holidays/export-csv/', views_csv.export_public_holidays_csv, name='export_public_holidays_csv'),
    path('holidays/import-csv/', views_csv.import_public_holidays_csv, name='import_public_holidays_csv'),
    path('holidays/sample-csv/', views_csv.download_public_holiday_sample_csv, name='download_public_holiday_sample_csv'),
    path('leave-types/', views.LeaveTypeListView.as_view(), name='leave_types'),
    path('leave-types/add/', views.LeaveTypeCreateView.as_view(), name='leave_type_add'),
    path('leave-types/<int:pk>/', views.LeaveTypeDetailView.as_view(), name='leave_type_detail'),
    path('leave-types/<int:pk>/edit/', views.LeaveTypeUpdateView.as_view(), name='leave_type_edit'),
    path('leave-types/<int:pk>/delete/', views.LeaveTypeDeleteView.as_view(), name='leave_type_delete'),
    path('leave-applications/', views.LeaveApplicationListView.as_view(), name='leave_application_list'),
    path('leave-application/add/', views.LeaveApplicationCreateView.as_view(), name='leave_application_add'),
    path('leave-application/<int:pk>/', views.LeaveApplicationDetailView.as_view(), name='leave_application_detail'),
    path('leave-application/<int:pk>/approve/', views.approve_leave, name='approve_leave'),
    path('leave-application/<int:pk>/reject/', views.reject_leave, name='reject_leave'),

    # User Management
    path('users/', views_user_management.UserListView.as_view(), name='user_list'),
    path('users/add/', views_user_management.UserCreateView.as_view(), name='create_user'),
    path('users/<int:pk>/profile/', views_user_management.UserProfileUpdateView.as_view(), name='edit_user_profile'),
    path('users/<int:pk>/delete/', views_user_management.UserDeleteView.as_view(), name='delete_user'),
    path('users/<int:user_id>/create-profile/', views_user_management.create_user_profile, name='create_user_profile'),
    path('users/<int:user_id>/assign-role/', views_user_management.assign_role, name='assign_role'),
    path('users/credentials/', views_user_management.UserCredentialsAPIView.as_view(), name='user_credentials_api'),
    path('users/credentials-collection/', views_user_management.UserCredentialsCollectionView.as_view(), name='user_credentials_collection'),
    path('my-profile/', views_user_management.my_profile, name='my_profile'),

    # Job & Recruitment Management
    path('jobs/', views_job.JobDescriptionListView.as_view(), name='job_list'),
    path('jobs/add/', views_job.JobDescriptionCreateView.as_view(), name='job_create'),
    path('jobs/<int:pk>/', views_job.JobDescriptionDetailView.as_view(), name='job_detail'),
    path('jobs/<int:pk>/edit/', views_job.JobDescriptionUpdateView.as_view(), name='job_edit'),
    path('jobs/<int:pk>/delete/', views_job.JobDescriptionDeleteView.as_view(), name='job_delete'),

    # Job Description CSV Import/Export
    path('jobs/export-csv/', views_csv.export_job_descriptions_csv, name='export_job_descriptions_csv'),
    path('jobs/import-csv/', views_csv.import_job_descriptions_csv, name='import_job_descriptions_csv'),
    path('jobs/sample-csv/', views_csv.download_job_description_sample_csv, name='download_job_description_sample_csv'),
    path('jobs/apply/', views_job_app.add_job_application_view, name='add_job_application'),
    path('jobs/application/success/', views_job_app.job_application_success_view, name='job_application_success'),
    path('candidates/', views_job.JobApplicationListView.as_view(), name='candidate_list'),
    path('candidates/<int:pk>/', views_job.JobApplicationDetailView.as_view(), name='candidate_detail'),
    path('candidates/tracker/', views_job.CandidateTrackerView.as_view(), name='candidate_tracker'),

    # Interview Management
    path('candidates/<int:application_id>/interview/add/', views_job.add_interview, name='add_interview'),
    path('interview/<int:interview_id>/edit/', views_job.edit_interview, name='edit_interview'),
    path('interview/<int:interview_id>/delete/', views_job.delete_interview, name='delete_interview'),
    path('candidates/interview/', views_job.InterviewScheduleView.as_view(), name='interview_schedule'),
    path('openings/', views_job.CurrentOpeningsView.as_view(), name='current_openings'),

    # Notifications & Messages
    path('notifications/create/', views_notifications.create_notification, name='create_notification'),
    path('messages/create/', views_notifications.create_message, name='create_message'),

    # System Management

    # System Details
    path('system/details/', views_system.SystemDetailListView.as_view(), name='system_detail_list'),
    path('system/details/add/', views_system.SystemDetailCreateView.as_view(), name='system_detail_add'),
    path('system/details/<int:pk>/', views_system.SystemDetailDetailView.as_view(), name='system_detail_view'),
    path('system/details/<int:pk>/edit/', views_system.SystemDetailUpdateView.as_view(), name='system_detail_edit'),
    path('system/details/<int:pk>/delete/', views_system.SystemDetailDeleteView.as_view(), name='system_detail_delete'),

    # MAC Address Management
    path('system/mac-addresses/', views_system.MacAddressListView.as_view(), name='mac_address_list'),
    path('system/mac-addresses/add/', views_system.MacAddressCreateView.as_view(), name='mac_address_add'),
    path('system/mac-addresses/<int:pk>/', views_system.MacAddressDetailView.as_view(), name='mac_address_view'),
    path('system/mac-addresses/<int:pk>/edit/', views_system.MacAddressUpdateView.as_view(), name='mac_address_edit'),
    path('system/mac-addresses/<int:pk>/delete/', views_system.MacAddressDeleteView.as_view(), name='mac_address_delete'),

    # System Requirements
    path('system/requirements/', views_system.SystemRequirementListView.as_view(), name='system_requirement_list'),
    path('system/requirements/add/', views_system.SystemRequirementCreateView.as_view(), name='system_requirement_add'),
    path('system/requirements/<int:pk>/edit/', views_system.SystemRequirementUpdateView.as_view(), name='system_requirement_edit'),
    path('system/requirements/<int:pk>/delete/', views_system.SystemRequirementDeleteView.as_view(), name='system_requirement_delete'),
    path('system/requirements/<int:pk>/approve/', views_system.approve_system_requirement, name='approve_system_requirement'),
    path('system/requirements/<int:pk>/reject/', views_system.reject_system_requirement, name='reject_system_requirement'),

    # Account Management
    path('account-management/', views_account_management.account_management, name='account_management'),
    path('account-management/create/', views_account_management.account_create, name='account_create'),
    path('account-management/<int:pk>/edit/', views_account_management.account_edit, name='account_edit'),
    path('account-management/<int:pk>/delete/', views_account_management.account_delete, name='account_delete'),
    path('account-management/import/', views_account_management.account_import_csv, name='account_import_csv'),
    path('account-management/export/', views_account_management.account_export_csv, name='account_export_csv'),
    path('account-management/sample/', views_account_management.account_sample_csv, name='account_sample_csv'),
    path('account-management/bulk-delete/', views_account_management.account_bulk_delete, name='account_bulk_delete'),
    path('account-management/bulk-export/', views_account_management.account_bulk_export, name='account_bulk_export'),

    # System Management Dashboard
    path('system-management/', views_system_management.system_management, name='system_management'),
    path('api/system-details/', views_system_management.get_system_details, name='api_system_details'),
    path('api/employees-for-assignment/', views_system_management.get_employees_for_assignment, name='api_employees_for_assignment'),
    path('api/assign-system/', views_system_management.assign_system, name='api_assign_system'),
    path('api/mac-systems-assignments/', views_system_management.get_mac_systems_assignments, name='api_mac_systems_assignments'),
    path('api/windows-systems-assignments/', views_system_management.get_windows_systems_assignments, name='api_windows_systems_assignments'),
    path('export/mac-systems-csv/', views_system_management.export_mac_systems_csv, name='export_mac_systems_csv'),
    path('export/windows-systems-csv/', views_system_management.export_windows_systems_csv, name='export_windows_systems_csv'),

]

