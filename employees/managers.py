from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone


class BaseManager(models.Manager):
    """
    Base manager with common CRUD operations
    """
    
    def get_or_none(self, **kwargs):
        """Get object or return None"""
        try:
            return self.get(**kwargs)
        except self.model.DoesNotExist:
            return None
    
    def get_active(self):
        """Get all active objects"""
        return self.filter(is_active=True)
    
    def get_inactive(self):
        """Get all inactive objects"""
        return self.filter(is_active=False)
    
    def search(self, query, fields=None):
        """Search objects in specified fields"""
        if not query:
            return self.all()
        
        if not fields:
            # Default fields to search in
            fields = ['name', 'description']
        
        from django.db.models import Q
        q_objects = Q()
        for field in fields:
            q_objects |= Q(**{f"{field}__icontains": query})
        
        return self.filter(q_objects)
    
    def bulk_create_with_timestamps(self, objs):
        """Bulk create with proper timestamps"""
        return self.bulk_create(objs)
    
    def bulk_update_with_timestamps(self, objs, fields):
        """Bulk update with proper timestamps"""
        return self.bulk_update(objs, fields)


class SoftDeleteManager(BaseManager):
    """
    Manager for models with soft delete functionality
    """
    
    def get_queryset(self):
        """Only return non-deleted objects by default"""
        return super().get_queryset().filter(deleted_at__isnull=True)
    
    def all_with_deleted(self):
        """Include deleted objects"""
        return super().get_queryset()
    
    def deleted_only(self):
        """Get only deleted objects"""
        return super().get_queryset().filter(deleted_at__isnull=False)
    
    def restore_by_id(self, pk):
        """Restore object by primary key"""
        obj = self.deleted_only().filter(pk=pk).first()
        if obj:
            obj.restore()
        return obj


class HierarchicalManager(BaseManager):
    """
    Manager for hierarchical models (parent/child relationships)
    """
    
    def roots(self):
        """Get all root nodes (objects without parents)"""
        return self.filter(parent__isnull=True)
    
    def leaves(self):
        """Get all leaf nodes (objects without children)"""
        return self.filter(children__isnull=True)
    
    def get_tree(self):
        """Get complete tree structure"""
        roots = self.roots()
        tree = []
        for root in roots:
            tree.append(self._build_subtree(root))
        return tree
    
    def _build_subtree(self, node):
        """Build subtree for a given node"""
        subtree = {
            'node': node,
            'children': []
        }
        children = node.children.all()
        for child in children:
            subtree['children'].append(self._build_subtree(child))
        return subtree


class UserManager(BaseManager):
    """
    Manager for User model with additional methods
    """
    
    def get_by_username_or_email(self, identifier):
        """Get user by username or email"""
        from django.db.models import Q
        return self.filter(
            Q(username__iexact=identifier) | Q(email__iexact=identifier)
        ).first()
    
    def get_active_users(self):
        """Get all active users"""
        return self.filter(is_active=True)
    
    def get_staff_users(self):
        """Get all staff users"""
        return self.filter(is_staff=True)
    
    def get_superusers(self):
        """Get all superusers"""
        return self.filter(is_superuser=True)
    
    def get_regular_users(self):
        """Get regular (non-superuser) users"""
        return self.filter(is_superuser=False)
    
    def search_users(self, query):
        """Search users by username, email, first name, or last name"""
        if not query:
            return self.all()
        
        from django.db.models import Q
        return self.filter(
            Q(username__icontains=query) |
            Q(email__icontains=query) |
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query)
        )
    
    def create_user_with_profile(self, username, email, password, role='employee', department=None, **kwargs):
        """Create user with profile in one transaction"""
        from django.contrib.auth.models import User
        from django.db import transaction
        
        try:
            with transaction.atomic():
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password,
                    **kwargs
                )
                
                from .models import UserProfile
                UserProfile.objects.create(
                    user=user,
                    role=role,
                    department=department
                )
                
                return user
        except Exception as e:
            raise ValidationError(f"Failed to create user: {str(e)}")


class DepartmentManager(BaseManager):
    """
    Manager for Department model
    """
    
    def get_with_head(self):
        """Get departments with their heads"""
        return self.select_related('head').all()
    
    def get_without_head(self):
        """Get departments without heads"""
        return self.filter(head__isnull=True)
    
    def assign_head(self, department_id, employee_id):
        """Assign head to department"""
        department = self.get(pk=department_id)
        from .models import Employee
        employee = Employee.objects.get(pk=employee_id)
        department.head = employee
        department.save()
        return department


class EmployeeManager(BaseManager):
    """
    Manager for Employee model
    """
    
    def get_by_department(self, department):
        """Get employees by department"""
        return self.filter(department=department)
    
    def get_by_designation(self, designation):
        """Get employees by designation"""
        return self.filter(designation=designation)
    
    def get_active_employees(self):
        """Get active employees"""
        return self.filter(is_active=True)
    
    def search_employees(self, query):
        """Search employees by various fields"""
        if not query:
            return self.all()
        
        from django.db.models import Q
        return self.filter(
            Q(employee_code__icontains=query) |
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(email__icontains=query) |
            Q(phone__icontains=query) |
            Q(department__name__icontains=query) |
            Q(designation__name__icontains=query)
        )
    
    def get_employees_by_role(self, role):
        """Get employees by profile role"""
        return self.filter(profile__role=role).select_related('profile')
