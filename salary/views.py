from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_POST
from django.db.models import Q
from datetime import datetime, date
from decimal import Decimal

from .models import SalaryStructure, EmployeeSalaryStructure, SalarySlip, SalaryHistory
from .forms import (
    SalaryStructureForm, EmployeeSalaryStructureForm,
    SalarySlipForm, SalaryHistoryForm, CTCCalculatorForm
)
from employees.models import Employee


# ============= Salary Structure Views =============

@login_required
def salary_structure_list(request):
    """List all salary structures"""
    structures = SalaryStructure.objects.all()
    
    context = {
        'structures': structures,
        'page_title': 'Salary Structures'
    }
    return render(request, 'salary/structure_list.html', context)


@login_required
def salary_structure_create(request):
    """Create new salary structure"""
    if request.method == 'POST':
        form = SalaryStructureForm(request.POST)
        if form.is_valid():
            structure = form.save()
            messages.success(request, f'Salary structure "{structure.name}" created successfully!')
            return redirect('salary:structure_list')
    else:
        form = SalaryStructureForm()
    
    context = {
        'form': form,
        'page_title': 'Create Salary Structure',
        'action': 'Create'
    }
    return render(request, 'salary/structure_form.html', context)


@login_required
def salary_structure_edit(request, pk):
    """Edit salary structure"""
    structure = get_object_or_404(SalaryStructure, pk=pk)
    
    if request.method == 'POST':
        form = SalaryStructureForm(request.POST, instance=structure)
        if form.is_valid():
            form.save()
            messages.success(request, 'Salary structure updated successfully!')
            return redirect('salary:structure_list')
    else:
        form = SalaryStructureForm(instance=structure)
    
    context = {
        'form': form,
        'structure': structure,
        'page_title': 'Edit Salary Structure',
        'action': 'Update'
    }
    return render(request, 'salary/structure_form.html', context)


@login_required
def salary_structure_delete(request, pk):
    """Delete salary structure"""
    structure = get_object_or_404(SalaryStructure, pk=pk)
    
    if request.method == 'POST':
        structure.delete()
        messages.success(request, 'Salary structure deleted successfully!')
        return redirect('salary:structure_list')
    
    context = {
        'structure': structure,
        'page_title': 'Delete Salary Structure'
    }
    return render(request, 'salary/structure_confirm_delete.html', context)


# ============= CTC Calculator =============

@login_required
def ctc_calculator(request):
    """CTC Calculator with live preview"""
    form = CTCCalculatorForm()
    breakdown = None
    
    if request.method == 'POST':
        form = CTCCalculatorForm(request.POST)
        if form.is_valid():
            ctc = form.cleaned_data['ctc']
            structure = form.cleaned_data['salary_structure']
            breakdown = structure.calculate_components(ctc)
    
    context = {
        'form': form,
        'breakdown': breakdown,
        'page_title': 'CTC Calculator'
    }
    return render(request, 'salary/ctc_calculator.html', context)


@login_required
@require_POST
def calculate_ctc_ajax(request):
    """AJAX endpoint for CTC calculation"""
    try:
        ctc = Decimal(request.POST.get('ctc', 0))
        structure_id = request.POST.get('structure_id')
        
        structure = SalaryStructure.objects.get(id=structure_id)
        breakdown = structure.calculate_components(ctc)
        
        # Convert Decimal to float for JSON serialization
        def decimal_to_float(obj):
            if isinstance(obj, dict):
                return {k: decimal_to_float(v) for k, v in obj.items()}
            elif isinstance(obj, Decimal):
                return float(obj)
            return obj
        
        breakdown = decimal_to_float(breakdown)
        
        return JsonResponse({'success': True, 'breakdown': breakdown})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


# ============= Employee Salary Assignment =============

@login_required
def employee_salary_list(request):
    """List all employee salary assignments"""
    assignments = EmployeeSalaryStructure.objects.select_related(
        'employee', 'salary_structure'
    ).filter(is_active=True)
    
    # Filter by employee
    employee_id = request.GET.get('employee')
    if employee_id:
        assignments = assignments.filter(employee_id=employee_id)
    
    context = {
        'assignments': assignments,
        'employees': Employee.objects.filter(employment_status__in=['probation', 'confirmed']),
        'page_title': 'Employee Salary Assignments'
    }
    return render(request, 'salary/employee_salary_list.html', context)


@login_required
def employee_salary_assign(request):
    """Assign salary structure to employee"""
    if request.method == 'POST':
        form = EmployeeSalaryStructureForm(request.POST)
        if form.is_valid():
            assignment = form.save(commit=False)
            assignment.created_by = request.user
            assignment.save()
            
            # Create salary history entry
            SalaryHistory.objects.create(
                employee=assignment.employee,
                new_ctc=assignment.ctc,
                reason='Salary Structure Assignment',
                effective_date=assignment.effective_from,
                created_by=request.user
            )
            
            messages.success(request, f'Salary structure assigned to {assignment.employee.full_name}!')
            return redirect('salary:employee_salary_list')
    else:
        form = EmployeeSalaryStructureForm()
    
    context = {
        'form': form,
        'page_title': 'Assign Salary Structure',
        'action': 'Assign'
    }
    return render(request, 'salary/employee_salary_form.html', context)


@login_required
def employee_salary_edit(request, pk):
    """Edit employee salary assignment"""
    assignment = get_object_or_404(EmployeeSalaryStructure, pk=pk)
    old_ctc = assignment.ctc
    
    if request.method == 'POST':
        form = EmployeeSalaryStructureForm(request.POST, instance=assignment)
        if form.is_valid():
            assignment = form.save()
            
            # Create history if CTC changed
            if old_ctc != assignment.ctc:
                SalaryHistory.objects.create(
                    employee=assignment.employee,
                    previous_ctc=old_ctc,
                    new_ctc=assignment.ctc,
                    reason='Salary Structure Update',
                    effective_date=assignment.effective_from,
                    created_by=request.user
                )
            
            messages.success(request, 'Salary assignment updated successfully!')
            return redirect('salary:employee_salary_list')
    else:
        form = EmployeeSalaryStructureForm(instance=assignment)
    
    context = {
        'form': form,
        'assignment': assignment,
        'page_title': 'Edit Salary Assignment',
        'action': 'Update'
    }
    return render(request, 'salary/employee_salary_form.html', context)


# ============= Salary Slip Generation =============

@login_required
def salary_slip_list(request):
    """List all salary slips"""
    slips = SalarySlip.objects.select_related('employee').all()
    
    # Filters
    month = request.GET.get('month')
    year = request.GET.get('year')
    employee_id = request.GET.get('employee')
    department_id = request.GET.get('department')
    
    if month:
        slips = slips.filter(month=month)
    if year:
        slips = slips.filter(year=year)
    if employee_id:
        slips = slips.filter(employee_id=employee_id)
    if department_id:
        slips = slips.filter(employee__department_id=department_id)
    
    context = {
        'slips': slips,
        'employees': Employee.objects.filter(employment_status__in=['probation', 'confirmed']),
        'page_title': 'Salary Slips'
    }
    return render(request, 'salary/slip_list.html', context)


@login_required
def salary_slip_generate(request):
    """Generate salary slip"""
    if request.method == 'POST':
        form = SalarySlipForm(request.POST)
        if form.is_valid():
            employee = form.cleaned_data['employee']
            month = form.cleaned_data['month']
            year = form.cleaned_data['year']
            
            # Check if slip already exists
            existing_slip = SalarySlip.objects.filter(
                employee=employee, month=month, year=year
            ).first()
            
            if existing_slip:
                messages.warning(request, 'Salary slip already exists for this period!')
                return redirect('salary:slip_detail', pk=existing_slip.pk)
            
            # Get active salary structure
            assignment = EmployeeSalaryStructure.objects.filter(
                employee=employee,
                is_active=True,
                effective_from__lte=date(year, month, 1)
            ).order_by('-effective_from').first()
            
            if not assignment:
                messages.error(request, 'No active salary structure found for this employee!')
                return redirect('salary:slip_generate')
            
            # Calculate components
            components = assignment.get_calculated_components()
            
            # Calculate LOP deduction
            total_working_days = form.cleaned_data['total_working_days']
            lop_days = form.cleaned_data['lop_days']
            lop_deduction = Decimal('0.00')
            
            if lop_days > 0:
                per_day_salary = components['gross_salary'] / Decimal(str(total_working_days))
                lop_deduction = (per_day_salary * Decimal(str(lop_days))).quantize(Decimal('0.01'))
            
            # Create salary slip
            slip = SalarySlip.objects.create(
                employee=employee,
                employee_salary_structure=assignment,
                month=month,
                year=year,
                total_working_days=total_working_days,
                days_present=form.cleaned_data['days_present'],
                days_absent=form.cleaned_data['days_absent'],
                lop_days=lop_days,
                basic_salary=components['earnings']['basic'],
                hra=components['earnings']['hra'],
                medical_allowance=components['earnings']['medical_allowance'],
                conveyance_allowance=components['earnings']['conveyance_allowance'],
                special_allowance=components['earnings']['special_allowance'],
                overtime_amount=form.cleaned_data.get('overtime_amount', 0),
                gross_salary=components['gross_salary'],
                employee_pf=components['employee_deductions']['pf'],
                employee_esic=components['employee_deductions']['esic'],
                professional_tax=components['employee_deductions']['professional_tax'],
                lop_deduction=lop_deduction,
                other_deductions=form.cleaned_data.get('other_deductions', 0),
                total_deductions=components['total_deductions'] + lop_deduction + form.cleaned_data.get('other_deductions', 0),
                net_salary=components['net_salary'] - lop_deduction - form.cleaned_data.get('other_deductions', 0) + form.cleaned_data.get('overtime_amount', 0),
                employer_pf=components['employer_contributions']['pf'],
                employer_esic=components['employer_contributions']['esic'],
                status='generated',
                generated_by=request.user
            )
            
            messages.success(request, 'Salary slip generated successfully!')
            return redirect('salary:slip_detail', pk=slip.pk)
    else:
        form = SalarySlipForm()
    
    context = {
        'form': form,
        'page_title': 'Generate Salary Slip'
    }
    return render(request, 'salary/slip_form.html', context)


@login_required
def salary_slip_detail(request, pk):
    """View salary slip details"""
    slip = get_object_or_404(SalarySlip, pk=pk)
    
    context = {
        'slip': slip,
        'page_title': f'Salary Slip - {slip.employee.full_name}'
    }
    return render(request, 'salary/slip_detail.html', context)


@login_required
def salary_slip_pdf(request, pk):
    """Generate PDF for salary slip"""
    from xhtml2pdf import pisa
    from django.template.loader import get_template
    
    slip = get_object_or_404(SalarySlip, pk=pk)
    
    template = get_template('salary/slip_pdf.html')
    context = {'slip': slip}
    html = template.render(context)
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="payslip_{slip.employee.employee_code}_{slip.month}_{slip.year}.pdf"'
    
    pisa_status = pisa.CreatePDF(html, dest=response)
    
    if pisa_status.err:
        return HttpResponse('Error generating PDF', status=500)
    
    return response


# ============= Salary History =============

@login_required
def salary_history_list(request, employee_id=None):
    """View salary history"""
    if employee_id:
        employee = get_object_or_404(Employee, pk=employee_id)
        history = SalaryHistory.objects.filter(employee=employee)
    else:
        employee = None
        history = SalaryHistory.objects.all()
    
    context = {
        'history': history,
        'employee': employee,
        'page_title': 'Salary History'
    }
    return render(request, 'salary/history_list.html', context)
