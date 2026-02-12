from django.contrib import admin
from django.contrib.auth.models import Group, User
from django.contrib.auth.admin import UserAdmin as DefaultUserAdmin
from django.utils.html import format_html
from .models import Department, Designation, EmergencyContact, Employee, EmployeeDocument, UserProfile, PublicHoliday
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
        # Python 3.14 compatibility fix - bypass Django's template system entirely
        from django.http import HttpResponse, HttpResponseRedirect
        from django.contrib import messages
        from django.middleware.csrf import get_token
        
        # Handle delete actions
        if request.method == 'POST':
            action = request.POST.get('action')
            selected_ids = request.POST.getlist('selected_ids')
            
            if action == 'delete_selected' and selected_ids:
                try:
                    deleted_count = 0
                    for obj_id in selected_ids:
                        obj = self.get_object(request, obj_id)
                        if obj:
                            obj.delete()
                            deleted_count += 1
                    messages.success(request, f'Successfully deleted {deleted_count} user profile(s).')
                except Exception as e:
                    messages.error(request, f'Error deleting user profiles: {str(e)}')
                return HttpResponseRedirect('/admin/employees/userprofile/')
            
            elif action.startswith('delete_'):
                obj_id = action.replace('delete_', '')
                try:
                    obj = self.get_object(request, obj_id)
                    if obj:
                        obj.delete()
                        messages.success(request, f'User profile for "{obj.user.username}" deleted successfully.')
                except Exception as e:
                    messages.error(request, f'Error deleting user profile: {str(e)}')
                return HttpResponseRedirect('/admin/employees/userprofile/')
        
        # Get queryset
        queryset = self.get_queryset(request)
        
        # Build simple HTML response
        html = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <title>User Profiles - HRMS Portal</title>
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
            <style>
                body {{ background-color: #f8f9fa; font-family: Arial, sans-serif; }}
                .navbar {{ background: #343a40; padding: 1rem 0; }}
                .navbar-brand {{ color: white; font-weight: bold; text-decoration: none; }}
                .container {{ max-width: 1200px; margin: 0 auto; padding: 20px; }}
                .card {{ background: white; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); padding: 20px; }}
                .table {{ width: 100%; border-collapse: collapse; }}
                .table th, .table td {{ padding: 12px; text-align: left; border-bottom: 1px solid #dee2e6; }}
                .table th {{ background: #f8f9fa; font-weight: bold; }}
                .btn {{ padding: 8px 16px; border: none; border-radius: 4px; text-decoration: none; display: inline-block; cursor: pointer; }}
                .btn-primary {{ background: #007bff; color: white; }}
                .btn-success {{ background: #28a745; color: white; }}
                .btn-danger {{ background: #dc3545; color: white; }}
                .btn:hover {{ opacity: 0.8; }}
                .header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }}
                .actions {{ display: flex; gap: 10px; }}
                .bulk-actions {{ background: #e9ecef; padding: 15px; border-radius: 4px; margin-bottom: 20px; }}
            </style>
        </head>
        <body>
            <nav class="navbar">
                <div class="container">
                    <a href="/admin/" class="navbar-brand">HRMS Portal</a>
                </div>
            </nav>
            
            <div class="container">
                <div class="card">
                    <div class="header">
                        <div>
                            <h2>User Profiles</h2>
                            <p class="text-muted">Manage user profiles and roles</p>
                        </div>
                        <a href="/admin/employees/userprofile/add/" class="btn btn-primary">Add User Profile</a>
                    </div>
                    
                    <form method="post">
                        <input type="hidden" name="csrfmiddlewaretoken" value="{get_token(request)}">
                        
                        <div class="bulk-actions">
                            <select name="action" class="form-control" style="width: 200px; display: inline-block;">
                                <option value="">Bulk Actions</option>
                                <option value="delete_selected">Delete Selected</option>
                            </select>
                            <button type="submit" class="btn btn-danger">Apply</button>
                        </div>
                        
                        <table class="table">
                            <thead>
                                <tr>
                                    <th><input type="checkbox" onchange="toggleAll(this)"></th>
                                    <th>User</th>
                                    <th>Role</th>
                                    <th>Department</th>
                                    <th>Phone</th>
                                    <th>Created</th>
                                    <th>Actions</th>
                                </tr>
                            </thead>
                            <tbody>
        """
        
        for profile in queryset:
            created_date = profile.created_at.strftime('%Y-%m-%d')
            department_name = profile.department.name if profile.department else '—'
            
            html += f"""
                                <tr>
                                    <td><input type="checkbox" name="selected_ids" value="{profile.id}"></td>
                                    <td><strong>{profile.user.username}</strong><br><small>{profile.user.get_full_name() or profile.user.email}</small></td>
                                    <td>{profile.get_role_display()}</td>
                                    <td>{department_name}</td>
                                    <td>{profile.phone or '—'}</td>
                                    <td>{created_date}</td>
                                    <td class="actions">
                                        <a href="/admin/employees/userprofile/{profile.id}/change/" class="btn btn-success">Edit</a>
                                        <button type="submit" name="action" value="delete_{profile.id}" class="btn btn-danger" 
                                                onclick="return confirm('Are you sure?')">Delete</button>
                                    </td>
                                </tr>
            """
        
        html += f"""
                            </tbody>
                        </table>
                    </form>
                </div>
            </div>
            
            <script>
                function toggleAll(source) {{
                    checkboxes = document.getElementsByName('selected_ids');
                    for(var i=0, n=checkboxes.length; i<n; i++) {{
                        checkboxes[i].checked = source.checked;
                    }}
                }}
            </script>
        </body>
        </html>
        """
        
        return HttpResponse(html)


@admin.register(Department)
class SimpleDepartmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'created_at']
    search_fields = ['name', 'description']
    list_filter = ['created_at']
    ordering = ['name']
    readonly_fields = ['created_at', 'updated_at']
    
    def changelist_view(self, request, extra_context=None):
        # Python 3.14 compatibility fix - bypass Django's template system entirely
        from django.http import HttpResponse, HttpResponseRedirect
        from django.contrib import messages
        from django.middleware.csrf import get_token
        
        # Handle delete actions
        if request.method == 'POST':
            action = request.POST.get('action')
            selected_ids = request.POST.getlist('selected_ids')
            
            if action == 'delete_selected' and selected_ids:
                try:
                    deleted_count = 0
                    for obj_id in selected_ids:
                        obj = self.get_object(request, obj_id)
                        if obj:
                            obj.delete()
                            deleted_count += 1
                    messages.success(request, f'Successfully deleted {deleted_count} department(s).')
                except Exception as e:
                    messages.error(request, f'Error deleting departments: {str(e)}')
                return HttpResponseRedirect('/admin/employees/department/')
            
            elif action.startswith('delete_'):
                obj_id = action.replace('delete_', '')
                try:
                    obj = self.get_object(request, obj_id)
                    if obj:
                        obj.delete()
                        messages.success(request, f'Department "{obj.name}" deleted successfully.')
                except Exception as e:
                    messages.error(request, f'Error deleting department: {str(e)}')
                return HttpResponseRedirect('/admin/employees/department/')
        
        # Get queryset
        queryset = self.get_queryset(request)
        
        # Build simple HTML response
        html = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <title>Departments - HRMS Portal</title>
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
            <style>
                body {{ background-color: #f8f9fa; font-family: Arial, sans-serif; }}
                .navbar {{ background: #343a40; padding: 1rem 0; }}
                .navbar-brand {{ color: white; font-weight: bold; text-decoration: none; }}
                .container {{ max-width: 1200px; margin: 0 auto; padding: 20px; }}
                .card {{ background: white; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); padding: 20px; }}
                .table {{ width: 100%; border-collapse: collapse; }}
                .table th, .table td {{ padding: 12px; text-align: left; border-bottom: 1px solid #dee2e6; }}
                .table th {{ background: #f8f9fa; font-weight: bold; }}
                .btn {{ padding: 8px 16px; border: none; border-radius: 4px; text-decoration: none; display: inline-block; cursor: pointer; }}
                .btn-primary {{ background: #007bff; color: white; }}
                .btn-success {{ background: #28a745; color: white; }}
                .btn-danger {{ background: #dc3545; color: white; }}
                .btn:hover {{ opacity: 0.8; }}
                .header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }}
                .actions {{ display: flex; gap: 10px; }}
                .bulk-actions {{ background: #e9ecef; padding: 15px; border-radius: 4px; margin-bottom: 20px; }}
            </style>
        </head>
        <body>
            <nav class="navbar">
                <div class="container">
                    <a href="/admin/" class="navbar-brand">HRMS Portal</a>
                </div>
            </nav>
            
            <div class="container">
                <div class="card">
                    <div class="header">
                        <div>
                            <h2>Departments</h2>
                            <p class="text-muted">Manage organizational departments</p>
                        </div>
                        <a href="/admin/employees/department/add/" class="btn btn-primary">Add Department</a>
                    </div>
                    
                    <form method="post">
                        <input type="hidden" name="csrfmiddlewaretoken" value="{get_token(request)}">
                        
                        <div class="bulk-actions">
                            <select name="action" class="form-control" style="width: 200px; display: inline-block;">
                                <option value="">Bulk Actions</option>
                                <option value="delete_selected">Delete Selected</option>
                            </select>
                            <button type="submit" class="btn btn-danger">Apply</button>
                        </div>
                        
                        <table class="table">
                            <thead>
                                <tr>
                                    <th><input type="checkbox" onchange="toggleAll(this)"></th>
                                    <th>Name</th>
                                    <th>Description</th>
                                    <th>Created</th>
                                    <th>Actions</th>
                                </tr>
                            </thead>
                            <tbody>
        """
        
        for dept in queryset:
            description = dept.description[:50] + "..." if dept.description and len(dept.description) > 50 else (dept.description or "")
            created_date = dept.created_at.strftime('%Y-%m-%d')
            
            html += f"""
                                <tr>
                                    <td><input type="checkbox" name="selected_ids" value="{dept.id}"></td>
                                    <td><strong>{dept.name}</strong></td>
                                    <td>{description or 'No description'}</td>
                                    <td>{created_date}</td>
                                    <td class="actions">
                                        <a href="/admin/employees/department/{dept.id}/change/" class="btn btn-success">Edit</a>
                                        <button type="submit" name="action" value="delete_{dept.id}" class="btn btn-danger" 
                                                onclick="return confirm('Are you sure?')">Delete</button>
                                    </td>
                                </tr>
            """
        
        html += f"""
                            </tbody>
                        </table>
                    </form>
                </div>
            </div>
            
            <script>
                function toggleAll(source) {{
                    checkboxes = document.getElementsByName('selected_ids');
                    for(var i=0, n=checkboxes.length; i<n; i++) {{
                        checkboxes[i].checked = source.checked;
                    }}
                }}
            </script>
        </body>
        </html>
        """
        
        return HttpResponse(html)
    
    def add_view(self, request, form_url='', extra_context=None):
        # Python 3.14 compatibility fix - bypass Django's template system entirely
        from django.http import HttpResponse, HttpResponseRedirect
        from django.contrib import messages
        from django.middleware.csrf import get_token
        
        if request.method == 'POST':
            form = self.get_form(request)
            if form.is_valid():
                obj = form.save()
                messages.success(request, f'Department "{obj.name}" added successfully.')
                return HttpResponseRedirect('/admin/employees/department/')
            else:
                messages.error(request, 'Please correct the errors below.')
        else:
            form = self.get_form(request)
        
        # Build simple HTML response
        html = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <title>Add Department - HRMS Portal</title>
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
            <style>
                body {{ background-color: #f8f9fa; font-family: Arial, sans-serif; }}
                .navbar {{ background: #343a40; padding: 1rem 0; }}
                .navbar-brand {{ color: white; font-weight: bold; text-decoration: none; }}
                .container {{ max-width: 800px; margin: 0 auto; padding: 20px; }}
                .card {{ background: white; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); padding: 30px; }}
                .form-group {{ margin-bottom: 20px; }}
                .form-label {{ font-weight: bold; margin-bottom: 8px; display: block; }}
                .form-control {{ width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 4px; }}
                .btn {{ padding: 10px 20px; border: none; border-radius: 4px; text-decoration: none; display: inline-block; cursor: pointer; }}
                .btn-primary {{ background: #007bff; color: white; }}
                .btn-secondary {{ background: #6c757d; color: white; }}
                .btn:hover {{ opacity: 0.8; }}
                .header {{ margin-bottom: 30px; }}
                .error {{ color: #dc3545; font-size: 14px; margin-top: 5px; }}
                .alert {{ padding: 15px; border-radius: 4px; margin-bottom: 20px; }}
                .alert-success {{ background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }}
                .alert-danger {{ background: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }}
            </style>
        </head>
        <body>
            <nav class="navbar">
                <div class="container">
                    <a href="/admin/" class="navbar-brand">HRMS Portal</a>
                </div>
            </nav>
            
            <div class="container">
                <div class="card">
                    <div class="header">
                        <h2>Add Department</h2>
                        <p class="text-muted">Create a new department</p>
                    </div>
                    
                    {self._get_messages_html(request)}
                    
                    <form method="post">
                        <input type="hidden" name="csrfmiddlewaretoken" value="{get_token(request)}">
                        
                        <div class="form-group">
                            <label class="form-label">Name *</label>
                            {form['name'].as_widget()}
                            {form['name'].errors}
                        </div>
                        
                        <div class="form-group">
                            <label class="form-label">Description</label>
                            {form['description'].as_widget()}
                            {form['description'].errors}
                        </div>
                        
                        <div class="form-group">
                            <button type="submit" class="btn btn-primary">Save Department</button>
                            <a href="/admin/employees/department/" class="btn btn-secondary">Cancel</a>
                        </div>
                    </form>
                </div>
            </div>
        </body>
        </html>
        """
        
        return HttpResponse(html)
    
    def change_view(self, request, object_id, form_url='', extra_context=None):
        # Python 3.14 compatibility fix - bypass Django's template system entirely
        from django.http import HttpResponse, HttpResponseRedirect
        from django.contrib import messages
        from django.middleware.csrf import get_token
        
        obj = self.get_object(request, object_id)
        if not obj:
            messages.error(request, 'Department not found.')
            return HttpResponseRedirect('/admin/employees/department/')
        
        if request.method == 'POST':
            form = self.get_form(request, obj)
            if form.is_valid():
                obj = form.save()
                messages.success(request, f'Department "{obj.name}" updated successfully.')
                return HttpResponseRedirect('/admin/employees/department/')
            else:
                messages.error(request, 'Please correct the errors below.')
        else:
            form = self.get_form(request, obj)
        
        # Build simple HTML response
        html = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <title>Change Department - HRMS Portal</title>
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
            <style>
                body {{ background-color: #f8f9fa; font-family: Arial, sans-serif; }}
                .navbar {{ background: #343a40; padding: 1rem 0; }}
                .navbar-brand {{ color: white; font-weight: bold; text-decoration: none; }}
                .container {{ max-width: 800px; margin: 0 auto; padding: 20px; }}
                .card {{ background: white; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); padding: 30px; }}
                .form-group {{ margin-bottom: 20px; }}
                .form-label {{ font-weight: bold; margin-bottom: 8px; display: block; }}
                .form-control {{ width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 4px; }}
                .btn {{ padding: 10px 20px; border: none; border-radius: 4px; text-decoration: none; display: inline-block; cursor: pointer; }}
                .btn-primary {{ background: #007bff; color: white; }}
                .btn-secondary {{ background: #6c757d; color: white; }}
                .btn-danger {{ background: #dc3545; color: white; }}
                .btn:hover {{ opacity: 0.8; }}
                .header {{ margin-bottom: 30px; }}
                .error {{ color: #dc3545; font-size: 14px; margin-top: 5px; }}
                .alert {{ padding: 15px; border-radius: 4px; margin-bottom: 20px; }}
                .alert-success {{ background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }}
                .alert-danger {{ background: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }}
                .readonly {{ background: #f8f9fa; color: #6c757d; }}
            </style>
        </head>
        <body>
            <nav class="navbar">
                <div class="container">
                    <a href="/admin/" class="navbar-brand">HRMS Portal</a>
                </div>
            </nav>
            
            <div class="container">
                <div class="card">
                    <div class="header">
                        <h2>Change Department</h2>
                        <p class="text-muted">Edit department: <strong>{obj.name}</strong></p>
                    </div>
                    
                    {self._get_messages_html(request)}
                    
                    <form method="post">
                        <input type="hidden" name="csrfmiddlewaretoken" value="{get_token(request)}">
                        
                        <div class="form-group">
                            <label class="form-label">Name *</label>
                            {form['name'].as_widget()}
                            {form['name'].errors}
                        </div>
                        
                        <div class="form-group">
                            <label class="form-label">Description</label>
                            {form['description'].as_widget()}
                            {form['description'].errors}
                        </div>
                        
                        <div class="form-group">
                            <label class="form-label">Created At</label>
                            <input type="text" class="form-control readonly" value="{obj.created_at.strftime('%Y-%m-%d %H:%M:%S')}" readonly>
                        </div>
                        
                        <div class="form-group">
                            <label class="form-label">Updated At</label>
                            <input type="text" class="form-control readonly" value="{obj.updated_at.strftime('%Y-%m-%d %H:%M:%S')}" readonly>
                        </div>
                        
                        <div class="form-group">
                            <button type="submit" class="btn btn-primary">Save Changes</button>
                            <a href="/admin/employees/department/" class="btn btn-secondary">Cancel</a>
                        </div>
                    </form>
                </div>
            </div>
        </body>
        </html>
        """
        
        return HttpResponse(html)
    
    def _get_messages_html(self, request):
        """Helper method to render Django messages as HTML"""
        from django.contrib.messages import get_messages
        messages_html = ""
        
        for message in get_messages(request):
            alert_class = {
                'success': 'alert-success',
                'error': 'alert-danger',
                'warning': 'alert-warning',
                'info': 'alert-info'
            }.get(message.tags, 'alert-info')
            
            messages_html += f'<div class="alert {alert_class}">{message}</div>'
        
        return messages_html


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
    
    def changelist_view(self, request, extra_context=None):
        # Python 3.14 compatibility fix - bypass Django's template system entirely
        from django.http import HttpResponse, HttpResponseRedirect
        from django.contrib import messages
        from django.middleware.csrf import get_token
        
        # Handle delete actions
        if request.method == 'POST':
            action = request.POST.get('action')
            selected_ids = request.POST.getlist('selected_ids')
            
            if action == 'delete_selected' and selected_ids:
                try:
                    deleted_count = 0
                    for obj_id in selected_ids:
                        obj = self.get_object(request, obj_id)
                        if obj:
                            obj.delete()
                            deleted_count += 1
                    messages.success(request, f'Successfully deleted {deleted_count} designation(s).')
                except Exception as e:
                    messages.error(request, f'Error deleting designations: {str(e)}')
                return HttpResponseRedirect('/admin/employees/designation/')
            
            elif action.startswith('delete_'):
                obj_id = action.replace('delete_', '')
                try:
                    obj = self.get_object(request, obj_id)
                    if obj:
                        obj.delete()
                        messages.success(request, f'Designation "{obj.name}" deleted successfully.')
                except Exception as e:
                    messages.error(request, f'Error deleting designation: {str(e)}')
                return HttpResponseRedirect('/admin/employees/designation/')
        
        # Get queryset
        queryset = self.get_queryset(request)
        
        # Build simple HTML response
        html = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <title>Designations - HRMS Portal</title>
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
            <style>
                body {{ background-color: #f8f9fa; font-family: Arial, sans-serif; }}
                .navbar {{ background: #343a40; padding: 1rem 0; }}
                .navbar-brand {{ color: white; font-weight: bold; text-decoration: none; }}
                .container {{ max-width: 1200px; margin: 0 auto; padding: 20px; }}
                .card {{ background: white; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); padding: 20px; }}
                .table {{ width: 100%; border-collapse: collapse; }}
                .table th, .table td {{ padding: 12px; text-align: left; border-bottom: 1px solid #dee2e6; }}
                .table th {{ background: #f8f9fa; font-weight: bold; }}
                .btn {{ padding: 8px 16px; border: none; border-radius: 4px; text-decoration: none; display: inline-block; cursor: pointer; }}
                .btn-primary {{ background: #007bff; color: white; }}
                .btn-success {{ background: #28a745; color: white; }}
                .btn-danger {{ background: #dc3545; color: white; }}
                .btn:hover {{ opacity: 0.8; }}
                .header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }}
                .actions {{ display: flex; gap: 10px; }}
                .bulk-actions {{ background: #e9ecef; padding: 15px; border-radius: 4px; margin-bottom: 20px; }}
            </style>
        </head>
        <body>
            <nav class="navbar">
                <div class="container">
                    <a href="/admin/" class="navbar-brand">HRMS Portal</a>
                </div>
            </nav>
            
            <div class="container">
                <div class="card">
                    <div class="header">
                        <div>
                            <h2>Designations</h2>
                            <p class="text-muted">Manage job designations and titles</p>
                        </div>
                        <a href="/admin/employees/designation/add/" class="btn btn-primary">Add Designation</a>
                    </div>
                    
                    <form method="post">
                        <input type="hidden" name="csrfmiddlewaretoken" value="{get_token(request)}">
                        
                        <div class="bulk-actions">
                            <select name="action" class="form-control" style="width: 200px; display: inline-block;">
                                <option value="">Bulk Actions</option>
                                <option value="delete_selected">Delete Selected</option>
                            </select>
                            <button type="submit" class="btn btn-danger">Apply</button>
                        </div>
                        
                        <table class="table">
                            <thead>
                                <tr>
                                    <th><input type="checkbox" onchange="toggleAll(this)"></th>
                                    <th>Name</th>
                                    <th>Department</th>
                                    <th>Description</th>
                                    <th>Created</th>
                                    <th>Actions</th>
                                </tr>
                            </thead>
                            <tbody>
        """
        
        for designation in queryset:
            description = designation.description[:50] + "..." if designation.description and len(designation.description) > 50 else (designation.description or "")
            created_date = designation.created_at.strftime('%Y-%m-%d')
            department_name = designation.department.name if designation.department else '—'
            
            html += f"""
                                <tr>
                                    <td><input type="checkbox" name="selected_ids" value="{designation.id}"></td>
                                    <td><strong>{designation.name}</strong></td>
                                    <td>{department_name}</td>
                                    <td>{description or 'No description'}</td>
                                    <td>{created_date}</td>
                                    <td class="actions">
                                        <a href="/admin/employees/designation/{designation.id}/change/" class="btn btn-success">Edit</a>
                                        <button type="submit" name="action" value="delete_{designation.id}" class="btn btn-danger" 
                                                onclick="return confirm('Are you sure?')">Delete</button>
                                    </td>
                                </tr>
            """
        
        html += f"""
                            </tbody>
                        </table>
                    </form>
                </div>
            </div>
            
            <script>
                function toggleAll(source) {{
                    checkboxes = document.getElementsByName('selected_ids');
                    for(var i=0, n=checkboxes.length; i<n; i++) {{
                        checkboxes[i].checked = source.checked;
                    }}
                }}
            </script>
        </body>
        </html>
        """
        
        return HttpResponse(html)


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
                   'employment_status_badge', 'probation_status_badge', 'period_type_badge', 'joining_date', 'mobile_number']
    list_filter = ['department', 'designation', 'employment_status', 'probation_status', 'period_type', 'joining_date']
    search_fields = ['employee_code', 'full_name', 'mobile_number', 'official_email']
    ordering = ['-created_at']
    inlines = [EmployeeDocumentInline]
    readonly_fields = ['probation_status', 'created_at', 'updated_at']
    
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
                      'total_experience_months', 'probation_status', 'period_type')
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
    
    def probation_status_badge(self, obj):
        color = 'orange' if 'Probation' in obj.probation_status else 'blue'
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.probation_status
        )
    probation_status_badge.short_description = 'Probation'
    probation_status_badge.admin_order_field = 'probation_status'
    
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
    
    def changelist_view(self, request, extra_context=None):
        # Python 3.14 compatibility fix - simple redirect to avoid template context issues
        from django.http import HttpResponse
        return HttpResponse("""
        <!DOCTYPE html>
        <html>
        <head><title>Employee Management - HRMS Portal</title></head>
        <body>
            <h1>Employee Management</h1>
            <p><strong>Python 3.14 Compatibility Mode:</strong> Employee management is temporarily using basic view.</p>
            <p><a href="/admin/">← Back to Admin</a></p>
            <p>Please use the Django admin interface for now, or contact administrator to enable full functionality.</p>
        </body>
        </html>
        """)


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
    
    def changelist_view(self, request, extra_context=None):
        # Python 3.14 compatibility fix - simple redirect to avoid template context issues
        from django.http import HttpResponse
        return HttpResponse("""
        <!DOCTYPE html>
        <html>
        <head><title>Employee Documents - HRMS Portal</title></head>
        <body>
            <h1>Employee Documents</h1>
            <p><strong>Python 3.14 Compatibility Mode:</strong> Document management is temporarily using basic view.</p>
            <p><a href="/admin/">← Back to Admin</a></p>
            <p>Please use the Django admin interface for now, or contact administrator to enable full functionality.</p>
        </body>
        </html>
        """)


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
