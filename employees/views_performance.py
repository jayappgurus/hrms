from django.shortcuts import render, get_object_or_404, redirect

from django.views.generic import ListView, DetailView

from django.contrib.auth.mixins import LoginRequiredMixin

from django.contrib import messages

from django.utils import timezone

from .models_performance import PerformanceEvaluation, EvaluationAuditLog

from .models import Department

from django.db.models import Q



class TraineeInternEvaluationDashboardView(LoginRequiredMixin, ListView):
    model = PerformanceEvaluation
    template_name = 'performance/trainee_intern_dashboard.html'
    context_object_name = 'evaluations'
    paginate_by = 20

    def get_queryset(self):
        queryset = PerformanceEvaluation.objects.filter(category='trainee_intern').select_related('employee', 'employee__department', 'assigned_manager')
        
        # Filters
        employee_name = self.request.GET.get('employee_name')
        department_id = self.request.GET.get('department')
        status = self.request.GET.get('status')
        cycle = self.request.GET.get('cycle')
        date_from = self.request.GET.get('date_from')
        date_to = self.request.GET.get('date_to')

        if employee_name:
            queryset = queryset.filter(employee__full_name__icontains=employee_name)
        if department_id:
            queryset = queryset.filter(employee__department_id=department_id)
        if status:
            if status == 'overdue':
                queryset = queryset.filter(status='pending', due_date__lt=timezone.now().date())
            else:
                queryset = queryset.filter(status=status)
        if cycle:
            queryset = queryset.filter(cycle_number=cycle)
        if date_from:
            queryset = queryset.filter(period_start__gte=date_from)
        if date_to:
            queryset = queryset.filter(period_end__lte=date_to)

        # Role-based access control
        user = self.request.user
        if hasattr(user, 'profile'):
            if user.profile.role == 'employee':
                queryset = queryset.filter(employee=user.profile.employee)
            elif user.profile.role == 'manager':
                # Show evaluations for their team or where they are assigned manager
                queryset = queryset.filter(Q(assigned_manager=user) | Q(employee__department__head=user.profile.employee))
        
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['departments'] = Department.objects.all()
        context['status_choices'] = PerformanceEvaluation.STATUS_CHOICES
        context['evaluation_type'] = 'Trainee/Intern'
        return context


class ProbationEvaluationDashboardView(LoginRequiredMixin, ListView):
    model = PerformanceEvaluation
    template_name = 'performance/probation_dashboard.html'
    context_object_name = 'evaluations'
    paginate_by = 20

    def get_queryset(self):
        queryset = PerformanceEvaluation.objects.filter(category='probation').select_related('employee', 'employee__department', 'assigned_manager')
        
        # Filters
        employee_name = self.request.GET.get('employee_name')
        department_id = self.request.GET.get('department')
        status = self.request.GET.get('status')
        cycle = self.request.GET.get('cycle')
        date_from = self.request.GET.get('date_from')
        date_to = self.request.GET.get('date_to')

        if employee_name:
            queryset = queryset.filter(employee__full_name__icontains=employee_name)
        if department_id:
            queryset = queryset.filter(employee__department_id=department_id)
        if status:
            if status == 'overdue':
                queryset = queryset.filter(status='pending', due_date__lt=timezone.now().date())
            else:
                queryset = queryset.filter(status=status)
        if cycle:
            queryset = queryset.filter(cycle_number=cycle)
        if date_from:
            queryset = queryset.filter(period_start__gte=date_from)
        if date_to:
            queryset = queryset.filter(period_end__lte=date_to)

        # Role-based access control
        user = self.request.user
        if hasattr(user, 'profile'):
            if user.profile.role == 'employee':
                queryset = queryset.filter(employee=user.profile.employee)
            elif user.profile.role == 'manager':
                # Show evaluations for their team or where they are assigned manager
                queryset = queryset.filter(Q(assigned_manager=user) | Q(employee__department__head=user.profile.employee))
        
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['departments'] = Department.objects.all()
        context['status_choices'] = PerformanceEvaluation.STATUS_CHOICES
        context['evaluation_type'] = 'Probation'
        return context


class EvaluationDashboardView(LoginRequiredMixin, ListView):

    model = PerformanceEvaluation

    template_name = 'performance/dashboard.html'

    context_object_name = 'evaluations'

    paginate_by = 20



    def get_queryset(self):

        queryset = PerformanceEvaluation.objects.select_related('employee', 'employee__department', 'assigned_manager')

        

        # Filters

        employee_name = self.request.GET.get('employee_name')

        department_id = self.request.GET.get('department')

        status = self.request.GET.get('status')

        cycle = self.request.GET.get('cycle')

        date_from = self.request.GET.get('date_from')

        date_to = self.request.GET.get('date_to')



        if employee_name:

            queryset = queryset.filter(employee__full_name__icontains=employee_name)

        if department_id:

            queryset = queryset.filter(employee__department_id=department_id)

        if status:

            if status == 'overdue':

                queryset = queryset.filter(status='pending', due_date__lt=timezone.now().date())

            else:

                queryset = queryset.filter(status=status)

        if cycle:

            queryset = queryset.filter(cycle_number=cycle)

        if date_from:

            queryset = queryset.filter(period_start__gte=date_from)

        if date_to:

            queryset = queryset.filter(period_end__lte=date_to)



        # Role-based access control

        user = self.request.user

        if hasattr(user, 'profile'):

            if user.profile.role == 'employee':

                queryset = queryset.filter(employee=user.profile.employee)

            elif user.profile.role == 'manager':

                # Show evaluations for their team or where they are assigned manager

                queryset = queryset.filter(Q(assigned_manager=user) | Q(employee__department__head=user.profile.employee))

        

        return queryset



    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        context['departments'] = Department.objects.all()

        context['status_choices'] = PerformanceEvaluation.STATUS_CHOICES

        return context



class EvaluationDetailView(LoginRequiredMixin, DetailView):

    model = PerformanceEvaluation

    template_name = 'performance/evaluation_form.html'

    context_object_name = 'evaluation'



    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        eval_obj = self.get_object()

        user = self.request.user

        

        # Check if user can edit

        can_edit = False

        if eval_obj.status in ['pending', 'rejected']:

            if hasattr(user, 'profile'):

                if user.profile.role in ['admin', 'hr', 'director']:

                    can_edit = True

                elif user.profile.role == 'manager' and eval_obj.assigned_manager == user:

                    can_edit = True

        

        context['can_edit'] = can_edit

        context['audit_logs'] = eval_obj.audit_logs.all()

        return context



def submit_evaluation(request, pk):

    evaluation = get_object_or_404(PerformanceEvaluation, pk=pk)

    if request.method == 'POST':

        # In a real scenario, we would save form fields here.

        # For now, we update the status.

        user = request.user

        if hasattr(user, 'profile'):

            if user.profile.role == 'manager':

                evaluation.status = 'submitted_manager'

            elif user.profile.role in ['hr', 'admin']:

                evaluation.status = 'submitted_hr'

            else:

                messages.error(request, "You are not authorized to submit this evaluation.")

                return redirect('employees:evaluation_detail', pk=pk)

        

        evaluation.submitted_at = timezone.now()

        evaluation.submitted_by = user

        evaluation.save()

        

        EvaluationAuditLog.objects.create(

            evaluation=evaluation,

            user=user,

            action='Submitted',

            details=f'Evaluation submitted by {user.get_full_name() or user.username}.'

        )

        messages.success(request, "Evaluation submitted successfully.")

    return redirect('employees:evaluation_detail', pk=pk)



def approve_evaluation(request, pk):

    evaluation = get_object_or_404(PerformanceEvaluation, pk=pk)

    user = request.user

    if not (hasattr(user, 'profile') and user.profile.role in ['admin', 'hr', 'director']):

        messages.error(request, "Only HR or Admin can approve evaluations.")

        return redirect('employees:evaluation_detail', pk=pk)

        

    evaluation.status = 'approved'

    evaluation.approved_at = timezone.now()

    evaluation.approved_by = user

    evaluation.save()

    

    EvaluationAuditLog.objects.create(

        evaluation=evaluation,

        user=user,

        action='Approved',

        details=f'Evaluation approved by {user.get_full_name() or user.username}.'

    )

    messages.success(request, "Evaluation approved successfully.")

    return redirect('employees:evaluation_detail', pk=pk)



def reject_evaluation(request, pk):

    evaluation = get_object_or_404(PerformanceEvaluation, pk=pk)

    user = request.user

    if not (hasattr(user, 'profile') and user.profile.role in ['admin', 'hr', 'director']):

        messages.error(request, "Only HR or Admin can reject evaluations.")

        return redirect('employees:evaluation_detail', pk=pk)

        

    reason = request.POST.get('rejection_reason', 'No reason provided.')

    evaluation.status = 'rejected'

    evaluation.rejection_reason = reason

    evaluation.save()

    

    EvaluationAuditLog.objects.create(

        evaluation=evaluation,

        user=user,

        action='Rejected',

        details=f'Evaluation rejected by {user.get_full_name() or user.username}. Reason: {reason}'

    )

    messages.success(request, "Evaluation rejected.")

    return redirect('employees:evaluation_detail', pk=pk)

