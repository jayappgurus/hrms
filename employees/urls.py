from django.urls import path
from . import views_job
from . import views_user_management
from . import views_department
from . import views
from . import views_auth
from . import views_job_application as views_job_app
from . import views_csv

app_name = 'employees'

urlpatterns = [
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
    path('update-document-status/<int:document_id>', 
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
    
    # Leave & Holiday Management
    path('holidays/', views.PublicHolidayListView.as_view(), name='public_holidays'),
    path('holidays/add/', views.PublicHolidayCreateView.as_view(), name='public_holiday_add'),
    path('holidays/<int:pk>/edit/', views.PublicHolidayUpdateView.as_view(), name='public_holiday_edit'),
    path('holidays/<int:pk>/delete/', views.PublicHolidayDeleteView.as_view(), name='public_holiday_delete'),
    
    # Public Holiday CSV Import/Export
    path('holidays/export-csv/', views_csv.export_public_holidays_csv, name='export_public_holidays_csv'),
    path('holidays/import-csv/', views_csv.import_public_holidays_csv, name='import_public_holidays_csv'),
    path('holidays/sample-csv/', views_csv.download_public_holiday_sample_csv, name='download_public_holiday_sample_csv'),
    
    path('leave-types/', views.LeaveTypeListView.as_view(), name='leave_types'),
    path('leave-types/add/', views.LeaveTypeCreateView.as_view(), name='leave_type_add'),
    path('leave-types/<int:pk>/edit/', views.LeaveTypeUpdateView.as_view(), name='leave_type_edit'),
    path('leave-types/<int:pk>/delete/', views.LeaveTypeDeleteView.as_view(), name='leave_type_delete'),
    path('leave-applications/', views.LeaveApplicationListView.as_view(), name='leave_application_list'),
    path('leave-application/add/', views.LeaveApplicationCreateView.as_view(), name='leave_application_add'),
    path('leave-application/<int:pk>/approve/', views.approve_leave, name='approve_leave'),
    path('leave-application/<int:pk>/reject/', views.reject_leave, name='reject_leave'),
    
    # User Management
    path('users/', views_user_management.UserListView.as_view(), name='user_list'),
    path('users/add/', views_user_management.UserCreateView.as_view(), name='create_user'),
    path('users/<int:pk>/profile/', views_user_management.UserProfileUpdateView.as_view(), name='edit_user_profile'),
    path('users/<int:pk>/delete/', views_user_management.UserDeleteView.as_view(), name='delete_user'),
    path('users/<int:user_id>/create-profile/', views_user_management.create_user_profile, name='create_user_profile'),
    path('users/<int:user_id>/assign-role/', views_user_management.assign_role, name='assign_role'),
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
]
