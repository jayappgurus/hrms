from django.urls import path
from . import views
from . import views_csv

app_name = 'leave'

urlpatterns = [
    # Public Holiday URLs
    path('holidays/', views.PublicHolidayListView.as_view(), name='public_holidays'),
    path('holidays/add/', views.PublicHolidayCreateView.as_view(), name='public_holiday_add'),
    path('holidays/<int:pk>/edit/', views.PublicHolidayUpdateView.as_view(), name='public_holiday_edit'),
    path('holidays/<int:pk>/delete/', views.PublicHolidayDeleteView.as_view(), name='public_holiday_delete'),
    path('holidays/<int:pk>/view/', views.PublicHolidayDetailView.as_view(), name='public_holiday_view'),
    
    # Public Holiday CSV Import/Export
    path('holidays/export-csv/', views_csv.export_public_holidays_csv, name='export_public_holidays_csv'),
    path('holidays/import-csv/', views_csv.import_public_holidays_csv, name='import_public_holidays_csv'),
    path('holidays/sample-csv/', views_csv.download_public_holiday_sample_csv, name='download_public_holiday_sample_csv'),
    
    # Leave Type URLs
    path('leave-types/', views.LeaveTypeListView.as_view(), name='leave_types'),
    path('leave-types/add/', views.LeaveTypeCreateView.as_view(), name='leave_type_add'),
    path('leave-types/<int:pk>/', views.LeaveTypeDetailView.as_view(), name='leave_type_detail'),
    path('leave-types/<int:pk>/edit/', views.LeaveTypeUpdateView.as_view(), name='leave_type_edit'),
    path('leave-types/<int:pk>/delete/', views.LeaveTypeDeleteView.as_view(), name='leave_type_delete'),
    
    # Leave Application URLs
    path('leave-applications/', views.LeaveApplicationListView.as_view(), name='leave_application_list'),
    path('leave-application/add/', views.LeaveApplicationCreateView.as_view(), name='leave_application_add'),
    path('leave-application/<int:pk>/', views.LeaveApplicationDetailView.as_view(), name='leave_application_detail'),
    path('leave-application/<int:pk>/approve/', views.approve_leave, name='approve_leave'),
    path('leave-application/<int:pk>/reject/', views.reject_leave, name='reject_leave'),
]
