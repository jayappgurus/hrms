# HRMS Portal - Model and View Abstractions

This document explains how to use the abstracted models, managers, mixins, and views for easier CRUD operations.

## 📁 Files Created

### 1. Abstract Models (`abstract_models.py`)
- **`TimeStampedModel`** - Base model with `created_at` and `updated_at` fields
- **`SoftDeleteModel`** - Adds soft delete functionality (`is_active`, `deleted_at`)
- **`UUIDModel`** - Base model with UUID primary key
- **`NameDescriptionModel`** - Base model with `name` and `description` fields
- **`HierarchicalModel`** - For parent/child relationships with tree operations
- **`CodeNameModel`** - Base model with `code` and `name` fields
- **`StatusModel`** - Base model with status field and status methods

### 2. Custom Managers (`managers.py`)
- **`BaseManager`** - Common CRUD operations (`get_or_none`, `search`, `bulk_create`, etc.)
- **`SoftDeleteManager`** - For soft delete models (`get_queryset`, `restore`, `deleted_only`)
- **`HierarchicalManager`** - For hierarchical models (`roots`, `leaves`, `get_tree`)
- **`UserManager`** - User-specific operations (`create_user_with_profile`, `search_users`)
- **`DepartmentManager`** - Department operations (`assign_head`, `get_with_head`)
- **`EmployeeManager`** - Employee operations (`search_employees`, `get_by_department`)

### 3. View Mixins (`mixins.py`)
- **Permission Mixins**: `StaffRequiredMixin`, `AdminRequiredMixin`, `SuperuserRequiredMixin`
- **Functionality Mixins**: `AJAXRequiredMixin`, `BulkOperationMixin`, `SearchMixin`
- **CRUD Mixins**: `TransactionMixin`, `ModalFormMixin`, `ExportMixin`
- **UI Mixins**: `PaginationMixin`, `FilterMixin`, `AuditMixin`

### 4. Base Views (`base_views.py`)
- **`BaseListView`** - List view with search, filter, pagination
- **`BaseCreateView`** - Create view with transactions and modal support
- **`BaseUpdateView`** - Update view with transactions and modal support
- **`BaseDetailView`** - Detail view
- **`BaseDeleteView`** - Delete view with confirmation
- **`BaseBulkOperationView`** - Bulk operations (delete, activate, deactivate)
- **`BaseExportView`** - Data export functionality
- **`BaseToggleStatusView`** - Toggle status functionality

## 🚀 Usage Examples

### Using Abstract Models

```python
# Instead of this:
class Department(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

# Use this:
class Department(NameDescriptionModel):
    head = models.ForeignKey('Employee', on_delete=models.SET_NULL, null=True)
    # Automatically gets: name, description, created_at, updated_at, __str__
```

### Using Custom Managers

```python
class Department(NameDescriptionModel):
    head = models.ForeignKey('Employee', on_delete=models.SET_NULL, null=True)
    
    objects = DepartmentManager()  # Use custom manager

# Usage:
departments = Department.objects.get_with_head()  # Get departments with heads
departments = Department.objects.get_without_head()  # Get departments without heads
Department.objects.assign_head(dept_id, employee_id)  # Assign head
```

### Using Mixins in Views

```python
from .mixins import StaffRequiredMixin, SearchMixin, BulkOperationMixin

class DepartmentListView(StaffRequiredMixin, SearchMixin, BulkOperationMixin, BaseListView):
    model = Department
    # Automatically gets: staff permission check, search functionality, bulk operations
```

### Using Base Views

```python
# Simple CRUD operations:
class DepartmentListView(BaseListView):
    model = Department
    # Automatically gets: pagination, search, filtering, context data

class DepartmentCreateView(BaseCreateView):
    model = Department
    fields = ['name', 'description']
    # Automatically gets: form validation, success messages, transactions

class DepartmentBulkOperationView(BaseBulkOperationView):
    model = Department
    # Automatically gets: bulk delete, activate, deactivate operations
```

## 📊 Benefits

### 1. Reduced Code Duplication
- Common functionality implemented once in base classes
- Consistent behavior across all CRUD operations
- Easy to maintain and update

### 2. Enhanced Functionality
- Built-in search, filtering, pagination
- Soft delete support
- Bulk operations out of the box
- Export functionality
- AJAX/modal support

### 3. Better Error Handling
- Transaction support for data integrity
- Consistent error messages
- Validation handling
- Audit logging capabilities

### 4. Improved Performance
- Optimized queries with `select_related`/`prefetch_related`
- Efficient bulk operations
- Caching support in managers
- Reduced database hits

## 🔧 Migration Guide

### Step 1: Update Models
```python
# Remove these fields from existing models:
created_at = models.DateTimeField(auto_now_add=True)
updated_at = models.DateTimeField(auto_now=True)
name = models.CharField(max_length=100)
description = models.TextField(blank=True, null=True)

# Replace with inheritance:
class Department(NameDescriptionModel):
    # Only add model-specific fields
    head = models.ForeignKey('Employee', on_delete=models.SET_NULL, null=True)
```

### Step 2: Update Views
```python
# Replace existing views with base classes:
from .base_views import BaseListView, BaseCreateView

class DepartmentListView(BaseListView):
    model = Department
    # Remove all boilerplate code
    
class DepartmentCreateView(BaseCreateView):
    model = Department
    fields = ['name', 'description', 'head']
    # Remove form_valid, get_context_data boilerplate
```

### Step 3: Add Custom Managers
```python
# Add to models:
from .managers import DepartmentManager

class Department(NameDescriptionModel):
    objects = DepartmentManager()  # Add custom manager
```

## 🎯 Best Practices

### 1. Model Design
- Use `NameDescriptionModel` for simple entities (Department, Designation)
- Use `SoftDeleteModel` for data that shouldn't be permanently deleted
- Use `HierarchicalModel` for tree structures
- Always define proper string representations

### 2. View Design
- Always use permission mixins (`StaffRequiredMixin`, etc.)
- Use `SearchMixin` for searchable lists
- Use `TransactionMixin` for data modifications
- Use `PaginationMixin` for large datasets

### 3. Manager Usage
- Use custom managers for complex queries
- Chain manager methods for fluent queries
- Use bulk operations for multiple records

### 4. Error Handling
- Always use transactions for multi-step operations
- Provide meaningful success/error messages
- Validate data before saving
- Handle edge cases gracefully

## 📝 Example: Complete CRUD Setup

```python
# models.py
class Department(NameDescriptionModel):
    head = models.ForeignKey('Employee', on_delete=models.SET_NULL, null=True)
    objects = DepartmentManager()

# views.py
class DepartmentListView(BaseListView):
    model = Department
    paginate_by = 15
    
    def get_queryset(self):
        return Department.objects.select_related('head').all()

class DepartmentCreateView(StaffRequiredMixin, BaseCreateView):
    model = Department
    fields = ['name', 'description', 'head']
    success_url = reverse_lazy('department_list')

# urls.py
urlpatterns = [
    path('departments/', DepartmentListView.as_view(), name='department_list'),
    path('departments/add/', DepartmentCreateView.as_view(), name='department_add'),
]
```

This setup provides:
- ✅ Automatic timestamps
- ✅ Search functionality
- ✅ Pagination
- ✅ Permission checking
- ✅ Transaction support
- ✅ Consistent UI
- ✅ Export capabilities
- ✅ Bulk operations

## 🔄 Next Steps

1. **Update existing models** to use abstract bases
2. **Replace existing views** with base view classes
3. **Add custom managers** to models
4. **Update URLs** to use new views
5. **Update templates** to use new context variables
6. **Test all CRUD operations** thoroughly
7. **Add comprehensive error handling**

This abstraction layer will significantly reduce development time and improve code quality across the HRMS portal.
