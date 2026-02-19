from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from .models_performance import PerformanceEvaluation

@login_required
def assign_manager(request, pk):
    """Assign a manager to an evaluation"""
    evaluation = get_object_or_404(PerformanceEvaluation, id=pk)
    
    if request.method == 'POST':
        manager_id = request.POST.get('manager_id')
        if manager_id:
            manager = get_object_or_404(User, id=manager_id)
            evaluation.assigned_manager = manager
            evaluation.save()
            messages.success(request, f'Manager {manager.get_full_name() or manager.username} assigned successfully.')
        else:
            evaluation.assigned_manager = None
            evaluation.save()
            messages.success(request, 'Manager assignment removed.')
        
        return redirect('employees:evaluation_detail', evaluation_id)
    
    # Get all users who can be managers (exclude superusers if needed)
    managers = User.objects.filter(is_active=True).exclude(is_superuser=True)
    
    return render(request, 'performance/assign_manager.html', {
        'evaluation': evaluation,
        'managers': managers,
        'current_manager': evaluation.assigned_manager
    })
