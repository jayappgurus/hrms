from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.db import transaction
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.views import View
from .mixins import (
    StaffRequiredMixin, AdminRequiredMixin, SearchMixin, FilterMixin,
    PaginationMixin, ExportMixin, TransactionMixin, ModalFormMixin,
    BulkOperationMixin
)
from .managers import BaseManager


class BaseListView(LoginRequiredMixin, SearchMixin, FilterMixin, PaginationMixin, ListView):
    """
    Base list view with search, filter, and pagination functionality
    """
    template_name_suffix = '_list'
    context_object_name = None
    paginate_by = 20
    
    def get_template_name(self):
        """Generate template name based on model"""
        if self.template_name:
            return self.template_name
        model_name = self.model._meta.model_name
        app_label = self.model._meta.app_label
        return f'{app_label}/{model_name}{self.template_name_suffix}.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if not self.context_object_name:
            self.context_object_name = f'{self.model._meta.model_name}s'
        context['title'] = f'{self.model._meta.verbose_name_plural.title()}'
        context['model_name'] = self.model._meta.model_name
        context['verbose_name'] = self.model._meta.verbose_name
        context['verbose_name_plural'] = self.model._meta.verbose_name_plural
        return context


class BaseCreateView(LoginRequiredMixin, TransactionMixin, ModalFormMixin, CreateView):
    """
    Base create view with transaction and modal support
    """
    template_name_suffix = '_form'
    
    def get_template_name(self):
        """Generate template name based on model"""
        if self.template_name:
            return self.template_name
        model_name = self.model._meta.model_name
        app_label = self.model._meta.app_label
        return f'{app_label}/{model_name}{self.template_name_suffix}.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Create {self.model._meta.verbose_name}'
        context['action'] = 'Create'
        context['model_name'] = self.model._meta.model_name
        context['verbose_name'] = self.model._meta.verbose_name
        return context
    
    def get_success_message(self):
        return f'{self.model._meta.verbose_name} created successfully!'


class BaseUpdateView(LoginRequiredMixin, TransactionMixin, ModalFormMixin, UpdateView):
    """
    Base update view with transaction and modal support
    """
    template_name_suffix = '_form'
    
    def get_template_name(self):
        """Generate template name based on model"""
        if self.template_name:
            return self.template_name
        model_name = self.model._meta.model_name
        app_label = self.model._meta.app_label
        return f'{app_label}/{model_name}{self.template_name_suffix}.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Edit {self.model._meta.verbose_name}'
        context['action'] = 'Edit'
        context['model_name'] = self.model._meta.model_name
        context['verbose_name'] = self.model._meta.verbose_name
        context['is_edit'] = True
        return context
    
    def get_success_message(self):
        return f'{self.model._meta.verbose_name} updated successfully!'


class BaseDetailView(LoginRequiredMixin, DetailView):
    """
    Base detail view
    """
    template_name_suffix = '_detail'
    
    def get_template_name(self):
        """Generate template name based on model"""
        if self.template_name:
            return self.template_name
        model_name = self.model._meta.model_name
        app_label = self.model._meta.app_label
        return f'{app_label}/{model_name}{self.template_name_suffix}.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = self.object
        context['model_name'] = self.model._meta.model_name
        context['verbose_name'] = self.model._meta.verbose_name
        return context


class BaseDeleteView(LoginRequiredMixin, DeleteView):
    """
    Base delete view with confirmation
    """
    template_name_suffix = '_confirm_delete'
    
    def get_template_name(self):
        """Generate template name based on model"""
        if self.template_name:
            return self.template_name
        model_name = self.model._meta.model_name
        app_label = self.model._meta.app_label
        return f'{app_label}/{model_name}{self.template_name_suffix}.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Delete {self.model._meta.verbose_name}'
        context['object_name'] = str(self.object)
        context['model_name'] = self.model._meta.model_name
        context['verbose_name'] = self.model._meta.verbose_name
        return context
    
    def delete(self, request, *args, **kwargs):
        """Override delete to add success message"""
        messages.success(request, f'{self.model._meta.verbose_name} deleted successfully!')
        return super().delete(request, *args, **kwargs)


class BaseBulkOperationView(LoginRequiredMixin, BulkOperationMixin, View):
    """
    Base view for bulk operations
    """
    model = None
    success_url = None
    
    def post(self, request, *args, **kwargs):
        """Handle bulk operations"""
        action = request.POST.get('action')
        selected_ids = request.POST.getlist('selected_ids')
        
        if not selected_ids:
            messages.error(request, 'No items selected.')
            return redirect(request.META.get('HTTP_REFERER', '/'))
        
        queryset = self.model.objects.filter(id__in=selected_ids)
        
        if action == 'delete':
            self.perform_bulk_delete(queryset)
        elif action == 'activate':
            self.perform_bulk_activate(queryset)
        elif action == 'deactivate':
            self.perform_bulk_deactivate(queryset)
        else:
            messages.error(request, 'Invalid action.')
        
        return redirect(request.META.get('HTTP_REFERER', '/'))


class BaseExportView(LoginRequiredMixin, ExportMixin, View):
    """
    Base view for data export
    """
    model = None
    
    def get(self, request, *args, **kwargs):
        """Handle export requests"""
        format_type = request.GET.get('format', 'csv')
        queryset = self.get_export_queryset()
        
        if format_type == 'csv':
            return self.export_to_csv(queryset)
        else:
            messages.error(request, 'Unsupported export format.')
            return redirect(request.META.get('HTTP_REFERER', '/'))
    
    def get_export_queryset(self):
        """Get queryset for export - to be overridden in subclasses"""
        return self.model.objects.all()


class BaseToggleStatusView(LoginRequiredMixin, View):
    """
    Base view for toggling status
    """
    model = None
    success_url = None
    
    def post(self, request, *args, **kwargs):
        """Handle status toggle"""
        obj = get_object_or_404(self.model, pk=kwargs['pk'])
        
        try:
            # Toggle the status
            obj.is_active = not obj.is_active
            obj.save()
            
            status_text = 'activated' if obj.is_active else 'deactivated'
            messages.success(request, f'{self.model._meta.verbose_name} {status_text} successfully!')
            
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')
        
        return redirect(request.META.get('HTTP_REFERER', self.success_url))


# Utility functions for common operations
def get_model_fields(model):
    """Get all field names for a model"""
    return [field.name for field in model._meta.get_fields()]


def get_model_choices(model, field_name):
    """Get choices for a model field"""
    try:
        field = model._meta.get_field(field_name)
        return field.choices if hasattr(field, 'choices') else []
    except:
        return []


def validate_unique_field(model, field_name, value, exclude_pk=None):
    """Validate uniqueness of a field"""
    queryset = model.objects.filter(**{field_name: value})
    if exclude_pk:
        queryset = queryset.exclude(pk=exclude_pk)
    
    if queryset.exists():
        raise ValidationError(f'{field_name} with this value already exists.')
    return True


def bulk_create_objects(model, objects_data):
    """Bulk create objects with validation"""
    created_objects = []
    errors = []
    
    try:
        with transaction.atomic():
            for obj_data in objects_data:
                try:
                    obj = model(**obj_data)
                    obj.full_clean()
                    obj.save()
                    created_objects.append(obj)
                except ValidationError as e:
                    errors.append(f"Error creating object: {str(e)}")
                except Exception as e:
                    errors.append(f"Unexpected error: {str(e)}")
    except Exception as e:
        errors.append(f"Transaction error: {str(e)}")
    
    return created_objects, errors
