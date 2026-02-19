from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Employee
from .models_performance import PerformanceEvaluation, EvaluationAuditLog
from datetime import timedelta, date
import calendar

def add_months(sourcedate, months):
    month = sourcedate.month - 1 + months
    year = sourcedate.year + month // 12
    month = month % 12 + 1
    day = min(sourcedate.day, calendar.monthrange(year, month)[1])
    return date(year, month, day)

@receiver(post_save, sender=Employee)
def handle_performance_evaluations(sender, instance, **kwargs):
    """
    Auto-create performance evaluations based on employee period type.
    Trainee/Intern: 3 cycles after every 2 months.
    Probation: 3 cycles, every month for 3 months.
    """
    if instance.period_type in ['trainee', 'intern']:
        create_evaluation_cycles(instance, 'trainee_intern', interval_months=2)
    elif instance.period_type == 'probation':
        create_evaluation_cycles(instance, 'probation', interval_months=1)

def create_evaluation_cycles(employee, category, interval_months):
    start_date = employee.joining_date
    if not start_date:
        return
        
    for i in range(1, 4):
        p_start = add_months(start_date, interval_months * (i-1))
        p_end = add_months(start_date, interval_months * i)
        d_date = p_end + timedelta(days=7) # Due date logic: 1 week after period ends
        
        eval_obj, created = PerformanceEvaluation.objects.get_or_create(
            employee=employee,
            category=category,
            cycle_number=i,
            defaults={
                'period_start': p_start,
                'period_end': p_end,
                'due_date': d_date,
                'status': 'pending'
            }
        )
        
        if created:
            EvaluationAuditLog.objects.create(
                evaluation=eval_obj,
                action='Created',
                details=f'Auto-created evaluation for cycle {i} based on {employee.get_period_type_display()}.'
            )
