# User Creation for Job Applications

## Overview
This guide explains how to create and link users to job applications in the HRMS portal.

## 🏗️ **User Model Structure**

We'll create a simple user model that can be linked to job applications:

```python
# employees/models_job.py (add this model)

class JobApplicationUser(models.Model):
    """User model for job applications"""
    username = models.CharField(max_length=150, unique=True, help_text="Username for application tracking")
    email = models.EmailField(unique=True, help_text="User email address")
    full_name = models.CharField(max_length=200, help_text="Full name of the user")
    phone_number = models.CharField(max_length=20, blank=True, null=True, help_text="Contact number")
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True, help_text="Whether this user account is active")
    
    class Meta:
        verbose_name = "Job Application User"
        verbose_name_plural = "Job Application Users"
        ordering = ['-created_at']
    
    def __str__(self):
        return self.full_name
```

## 📝 **Updated Job Application Form**

Update the application form to include user selection:

```html
<!-- In templates/jobs/add_job_application.html, add this section -->

<!-- User Selection -->
<div class="form-section">
    <div class="section-title">
        <i class="bi bi-person"></i>
        User Selection
    </div>
    
    <div class="candidate-grid">
        <div class="modern-form-group">
            <label class="modern-form-label required">Select User *</label>
            <select name="application_user" id="userSelect" class="modern-form-control modern-form-select" required>
                <option value="">Choose or create a user...</option>
                {% for user in available_users %}
                <option value="{{ user.id }}">{{ user.full_name }} ({{ user.email }})</option>
                {% endfor %}
                <option value="new_user">+ Create New User</option>
            </select>
            {% if form.application_user.errors %}
            <div class="text-danger small mt-1">{{ form.application_user.errors.0 }}</div>
            {% endif %}
        </div>
        
        <!-- Show new user form when "Create New User" is selected -->
        <div id="newUserForm" style="display: none;">
            <div class="modern-form-group">
                <label class="modern-form-label required">Full Name *</label>
                <input type="text" name="new_user_full_name" class="modern-form-control" placeholder="Enter full name">
            </div>
            <div class="modern-form-group">
                <label class="modern-form-label required">Email *</label>
                <input type="email" name="new_user_email" class="modern-form-control" placeholder="Enter email address">
            </div>
            <div class="modern-form-group">
                <label class="modern-form-label">Phone Number</label>
                <input type="tel" name="new_user_phone" class="modern-form-control" placeholder="Enter phone number">
            </div>
        </div>
    </div>
```

## 🔧 **Updated Backend View**

```python
# employees/views_job_application.py (update the view)

from .models_job import JobApplicationUser

@require_http_methods(["GET", "POST"])
def add_job_application_view(request):
    """Handle job application creation with candidate linking"""
    
    if request.method == 'POST':
        form = JobApplicationForm(request.POST, request.FILES)
        
        # Handle user selection
        application_user_id = request.POST.get('application_user')
        new_user_full_name = request.POST.get('new_user_full_name')
        new_user_email = request.POST.get('new_user_email')
        new_user_phone = request.POST.get('new_user_phone')
        
        # Create new user if needed
        if application_user_id == 'new_user' and new_user_full_name and new_user_email:
            try:
                new_user = JobApplicationUser.objects.create(
                    username=new_user_email,  # Use email as username
                    email=new_user_email,
                    full_name=new_user_full_name,
                    phone_number=new_user_phone
                )
                application_user_id = new_user.id
                messages.success(request, f'New user {new_user_full_name} created successfully!')
            except Exception as e:
                messages.error(request, f'Error creating user: {str(e)}')
                return redirect('employees:add_job_application')
        elif application_user_id:
            try:
                application_user = JobApplicationUser.objects.get(id=application_user_id)
            except JobApplicationUser.DoesNotExist:
                messages.error(request, 'Selected user not found.')
                return redirect('employees:add_job_application')
        else:
            messages.error(request, 'Please select a user or create a new one.')
            return redirect('employees:add_job_application')
        
        if form.is_valid():
            application = form.save(commit=False)
            
            # Link to the selected job
            job_id = request.POST.get('job')
            if job_id:
                try:
                    job = JobDescription.objects.get(pk=job_id, status='active')
                    application.job = job
                    application.application_user = application_user  # Link to user
                except JobDescription.DoesNotExist:
                    messages.error(request, 'Selected job not found or is not active.')
                    return redirect('employees:add_job_application')
            
            application.status = 'received'
            application.save()
            
            messages.success(request, f'Application submitted successfully for {job.title if job else "position"}!')
            return redirect('employees:job_application_success')
        else:
            messages.error(request, 'Please correct the errors below.')
            return render(request, 'jobs/add_job_application.html', {
                'form': form,
                'available_jobs': JobDescription.objects.filter(status='active').select_related('designation', 'department'),
                'available_users': JobApplicationUser.objects.filter(is_active=True).order_by('-created_at')
            })
    else:
        form = JobApplicationForm()
        return render(request, 'jobs/add_job_application.html', {
            'form': form,
            'available_jobs': JobDescription.objects.filter(status='active').select_related('designation', 'department'),
            'available_users': JobApplicationUser.objects.filter(is_active=True).order_by('-created_at')
        })
```

## 🎯 **Key Features**

### **User Management:**
- ✅ Create new users directly from application form
- ✅ Select from existing users
- ✅ Link applications to specific users
- ✅ User model with essential fields

### **Enhanced Application Form:**
- ✅ Dynamic user selection dropdown
- ✅ Inline new user creation form
- ✅ JavaScript form toggle for new user creation
- ✅ User validation and error handling

### **Application Tracking:**
- ✅ Applications are linked to specific users
- ✅ Better tracking and reporting
- ✅ User-based application management

## 🔄 **Usage Workflow**

```
HR Staff → Add Job Application → Select Existing User OR Create New User → Fill Application → Submit → Application linked to user and job
```

## 📊 **Benefits**

1. **Complete User Management**: Track which user submitted each application
2. **Flexible Application Process**: Can create users on-the-fly during application
3. **Better Organization**: Link applications to specific users for follow-up
4. **Enhanced Tracking**: Know which user submitted which application
5. **Professional Workflow**: Maintains clean separation between users and applications

## 🚀 **Implementation Steps**

1. **Create User Model** (shown above)
2. **Run Migration**: `python manage.py makemigrations` and `python manage.py migrate`
3. **Update Form Template** (shown above)
4. **Update Backend View** (shown above)
5. **Test the Complete Workflow**

This system provides a complete solution for managing job applications with user association and tracking capabilities.
