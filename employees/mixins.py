from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import JsonResponse
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import View
from django.db import transaction
import json


class StaffRequiredMixin(UserPassesTestMixin):
    """Mixin to restrict access to staff users only"""
    
    def test_func(self):
        return self.request.user.is_staff
    
    def handle_no_permission(self):
        messages.error(self.request, "You don't have permission to access this page.")
        return redirect('login')


class AdminRequiredMixin(UserPassesTestMixin):
    """Mixin to restrict access to admin users only"""
    
    def test_func(self):
        return self.request.user.is_superuser
    
    def handle_no_permission(self):
        messages.error(self.request, "Admin access required.")
        return redirect('login')


class SuperuserRequiredMixin(UserPassesTestMixin):
    """Mixin to restrict access to superusers only"""
    
    def test_func(self):
        return self.request.user.is_superuser
    
    def handle_no_permission(self):
        messages.error(self.request, "Superuser access required.")
        return redirect('login')


class AJAXRequiredMixin:
    """Mixin to handle AJAX requests"""
    
    def dispatch(self, request, *args, **kwargs):
        if not request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'error': 'AJAX required'}, status=400)
        return super().dispatch(request, *args, **kwargs)


class BulkOperationMixin:
    """Mixin for bulk operations on models"""
    
    def perform_bulk_delete(self, queryset):
        """Perform bulk delete on queryset"""
        count = queryset.count()
        queryset.delete()
        messages.success(self.request, f'Successfully deleted {count} items.')
    
    def perform_bulk_update(self, queryset, updates):
        """Perform bulk update on queryset"""
        count = queryset.count()
        queryset.update(**updates)
        messages.success(self.request, f'Successfully updated {count} items.')
    
    def perform_bulk_activate(self, queryset):
        """Perform bulk activate on queryset"""
        count = queryset.count()
        queryset.update(is_active=True)
        messages.success(self.request, f'Successfully activated {count} items.')
    
    def perform_bulk_deactivate(self, queryset):
        """Perform bulk deactivate on queryset"""
        count = queryset.count()
        queryset.update(is_active=False)
        messages.success(self.request, f'Successfully deactivated {count} items.')


class SearchMixin:
    """Mixin to handle search functionality"""
    
    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.request.GET.get('search', '').strip()
        
        if search_query:
            queryset = self._apply_search(queryset, search_query)
        
        return queryset
    
    def _apply_search(self, queryset, search_query):
        """Apply search to queryset - to be overridden in subclasses"""
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('search', '')
        return context


class FilterMixin:
    """Mixin to handle filtering functionality"""
    
    def get_queryset(self):
        queryset = super().get_queryset()
        return self._apply_filters(queryset)
    
    def _apply_filters(self, queryset):
        """Apply filters to queryset - to be overridden in subclasses"""
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filters'] = self._get_filter_params()
        return context
    
    def _get_filter_params(self):
        """Get filter parameters from request"""
        return {
            key: self.request.GET.get(key, '')
            for key in self.get_filter_fields()
        }
    
    def get_filter_fields(self):
        """Return list of filter field names - to be overridden in subclasses"""
        return []


class PaginationMixin:
    """Mixin to enhance pagination functionality"""
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        if hasattr(self, 'paginate_by') and self.paginate_by:
            page_obj = context.get('page_obj')
            if page_obj:
                context['pagination_info'] = {
                    'current_page': page_obj.number,
                    'total_pages': page_obj.paginator.num_pages,
                    'has_previous': page_obj.has_previous(),
                    'has_next': page_obj.has_next(),
                    'previous_page': page_obj.previous_page_number() if page_obj.has_previous() else None,
                    'next_page': page_obj.next_page_number() if page_obj.has_next() else None,
                    'total_items': page_obj.paginator.count,
                    'start_index': page_obj.start_index(),
                    'end_index': page_obj.end_index(),
                }
        
        return context


class ExportMixin:
    """Mixin to handle data export functionality"""
    
    def get_export_filename(self, format_type):
        """Generate filename for export"""
        model_name = self.model._meta.model_name
        timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
        return f'{model_name}_export_{timestamp}.{format_type}'
    
    def export_to_csv(self, queryset):
        """Export queryset to CSV"""
        import csv
        from django.http import HttpResponse
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="{self.get_export_filename("csv")}"'
        
        writer = csv.writer(response)
        # Write header
        headers = self.get_export_headers()
        writer.writerow(headers)
        
        # Write data
        for obj in queryset:
            row = self.get_export_row(obj, headers)
            writer.writerow(row)
        
        return response
    
    def get_export_headers(self):
        """Get headers for export - to be overridden in subclasses"""
        return []
    
    def get_export_row(self, obj, headers):
        """Get row data for export - to be overridden in subclasses"""
        return []


class TransactionMixin:
    """Mixin to handle database transactions"""
    
    def form_valid(self, form):
        try:
            with transaction.atomic():
                response = super().form_valid(form)
                messages.success(self.request, self.get_success_message())
                return response
        except Exception as e:
            messages.error(self.request, f'Error: {str(e)}')
            return self.form_invalid(form)
    
    def get_success_message(self):
        """Get success message - to be overridden in subclasses"""
        return 'Operation completed successfully.'


class AuditMixin:
    """Mixin to add audit logging functionality"""
    
    def form_valid(self, form):
        response = super().form_valid(form)
        self.log_action('create' if self.request.method == 'POST' else 'update', self.object)
        return response
    
    def delete(self, request, *args, **kwargs):
        response = super().delete(request, *args, **kwargs)
        self.log_action('delete', self.object)
        return response
    
    def log_action(self, action, obj):
        """Log action - to be overridden in subclasses"""
        pass


class ModalFormMixin:
    """Mixin to handle modal form submissions"""
    
    def form_valid(self, form):
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'message': self.get_success_message(),
                'redirect_url': self.get_success_url()
            })
        return super().form_valid(form)
    
    def form_invalid(self, form):
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'errors': form.errors,
                'message': 'Please correct the errors below.'
            })
        return super().form_invalid(form)
