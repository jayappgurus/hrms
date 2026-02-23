from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
import uuid


class TimeStampedModel(models.Model):
    """
    Abstract base model with created_at and updated_at fields
    """
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class SoftDeleteModel(TimeStampedModel):
    """
    Abstract base model with soft delete functionality
    """
    is_active = models.BooleanField(default=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        abstract = True

    def soft_delete(self):
        """Mark the object as deleted"""
        self.is_active = False
        self.deleted_at = timezone.now()
        self.save()

    def restore(self):
        """Restore the object"""
        self.is_active = True
        self.deleted_at = None
        self.save()

    def hard_delete(self):
        """Permanently delete the object"""
        super().delete()


class UUIDModel(TimeStampedModel):
    """
    Abstract base model with UUID primary key
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True


class NameDescriptionModel(TimeStampedModel):
    """
    Abstract base model with name and description fields
    """
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)

    class Meta:
        abstract = True
        ordering = ['name']

    def __str__(self):
        return self.name


class HierarchicalModel(NameDescriptionModel):
    """
    Abstract base model for hierarchical data (parent/child relationships)
    """
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')
    level = models.PositiveIntegerField(default=0)
    
    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        if self.parent:
            self.level = self.parent.level + 1
        else:
            self.level = 0
        super().save(*args, **kwargs)

    def get_ancestors(self):
        """Get all ancestors of this node"""
        ancestors = []
        current = self.parent
        while current:
            ancestors.append(current)
            current = current.parent
        return ancestors

    def get_descendants(self):
        """Get all descendants of this node"""
        return self.__class__.objects.filter(parent__in=self.get_all_children())

    def get_all_children(self):
        """Get all direct and indirect children"""
        children = []
        for child in self.children.all():
            children.append(child)
            children.extend(child.get_all_children())
        return children

    def is_root(self):
        """Check if this is a root node"""
        return self.parent is None

    def is_leaf(self):
        """Check if this is a leaf node"""
        return not self.children.exists()


class CodeNameModel(TimeStampedModel):
    """
    Abstract base model with code and name fields
    """
    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)

    class Meta:
        abstract = True
        ordering = ['code']

    def __str__(self):
        return f"{self.code} - {self.name}"


class StatusModel(TimeStampedModel):
    """
    Abstract base model with status field
    """
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')

    class Meta:
        abstract = True

    def is_active_status(self):
        """Check if status is active"""
        return self.status == 'active'

    def is_inactive_status(self):
        """Check if status is inactive"""
        return self.status == 'inactive'

    def activate(self):
        """Set status to active"""
        self.status = 'active'
        self.save()

    def deactivate(self):
        """Set status to inactive"""
        self.status = 'inactive'
        self.save()
