from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.core.paginator import Paginator
from django.http import HttpResponse
import csv
import io
from .models import AccountManagement
from .forms import AccountManagementForm


@login_required
def account_management(request):
    """
    View to display and manage account credentials
    """
    if not request.user.is_staff and not request.user.is_superuser:
        messages.error(request, 'You do not have permission to access account management.')
        return redirect('employees:dashboard')
    
    accounts = AccountManagement.objects.all()
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        accounts = accounts.filter(
            Q(name__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(teams__icontains=search_query) |
            Q(github__icontains=search_query)
        )
    
    # Pagination
    paginator = Paginator(accounts, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'accounts': page_obj,
        'search_query': search_query,
        'is_paginated': page_obj.has_other_pages(),
        'page_obj': page_obj,
    }
    
    return render(request, 'employees/account_management.html', context)


@login_required
def account_create(request):
    """
    View to create a new account entry
    """
    if not request.user.is_staff and not request.user.is_superuser:
        messages.error(request, 'You do not have permission to create accounts.')
        return redirect('employees:account_management')
    
    if request.method == 'POST':
        form = AccountManagementForm(request.POST)
        if form.is_valid():
            account = form.save()
            messages.success(request, f'Account for {account.name} has been created successfully.')
            return redirect('employees:account_management')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = AccountManagementForm()
    
    return render(request, 'employees/account_form.html', {
        'form': form,
        'title': 'Create New Account',
        'action': 'Create'
    })


@login_required
def account_edit(request, pk):
    """
    View to edit an existing account entry
    """
    if not request.user.is_staff and not request.user.is_superuser:
        messages.error(request, 'You do not have permission to edit accounts.')
        return redirect('employees:account_management')
    
    account = get_object_or_404(AccountManagement, pk=pk)
    
    if request.method == 'POST':
        form = AccountManagementForm(request.POST, instance=account)
        if form.is_valid():
            account = form.save()
            messages.success(request, f'Account for {account.name} has been updated successfully.')
            return redirect('employees:account_management')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = AccountManagementForm(instance=account)
    
    return render(request, 'employees/account_form.html', {
        'form': form,
        'account': account,
        'title': 'Edit Account',
        'action': 'Update'
    })


@login_required
def account_delete(request, pk):
    """
    View to delete an account entry
    """
    if not request.user.is_staff and not request.user.is_superuser:
        messages.error(request, 'You do not have permission to delete accounts.')
        return redirect('employees:account_management')
    
    account = get_object_or_404(AccountManagement, pk=pk)
    
    if request.method == 'POST':
        account_name = account.name
        account.delete()
        messages.success(request, f'Account for {account_name} has been deleted successfully.')
        return redirect('employees:account_management')
    
    return render(request, 'employees/account_confirm_delete.html', {
        'account': account
    })


@login_required
def account_import_csv(request):
    """
    View to import accounts from CSV file
    """
    if not request.user.is_staff and not request.user.is_superuser:
        messages.error(request, 'You do not have permission to import accounts.')
        return redirect('employees:account_management')
    
    if request.method == 'POST':
        try:
            csv_file = request.FILES.get('csv_file')
            if not csv_file:
                messages.error(request, 'Please select a CSV file.')
                return redirect('employees:account_management')
            
            # Check if file is CSV
            if not csv_file.name.endswith('.csv'):
                messages.error(request, 'Please upload a CSV file.')
                return redirect('employees:account_management')
            
            # Check file size (10MB limit)
            if csv_file.size > 10 * 1024 * 1024:
                messages.error(request, 'File size must be less than 10MB.')
                return redirect('employees:account_management')
            
            # Read and process CSV
            data_set = csv_file.read().decode('UTF-8')
            io_string = io.StringIO(data_set)
            next(io_string)  # Skip header row
            
            skip_duplicates = request.POST.get('skip_duplicates') == 'on'
            imported_count = 0
            skipped_count = 0
            
            for column in csv.reader(io_string):
                if len(column) >= 9:  # Ensure we have at least 9 columns
                    name = column[0].strip()
                    email = column[1].strip()
                    email_password = column[2].strip()
                    teams = column[3].strip() if column[3].strip() else ''
                    teams_password = column[4].strip() if column[4].strip() else ''
                    basecamp_password = column[5].strip() if column[5].strip() else ''
                    system_password = column[6].strip()
                    github = column[7].strip() if column[7].strip() else ''
                    github_password = column[8].strip() if column[8].strip() else ''
                    notes = column[9].strip() if len(column) > 9 and column[9].strip() else ''
                    
                    # Check for duplicates if requested
                    if skip_duplicates:
                        if AccountManagement.objects.filter(email=email).exists():
                            skipped_count += 1
                            continue
                    
                    # Create account
                    AccountManagement.objects.create(
                        name=name,
                        email=email,
                        email_password=email_password,
                        teams=teams,
                        teams_password=teams_password,
                        basecamp_password=basecamp_password,
                        system_password=system_password,
                        github=github,
                        github_password=github_password,
                        notes=notes,
                        is_active=True
                    )
                    imported_count += 1
            
            messages.success(request, f'Successfully imported {imported_count} accounts. {skipped_count} accounts were skipped.')
            
        except Exception as e:
            messages.error(request, f'Error importing CSV: {str(e)}')
    
    return redirect('employees:account_management')


@login_required
def account_export_csv(request):
    """
    View to export accounts to CSV file
    """
    if not request.user.is_staff and not request.user.is_superuser:
        messages.error(request, 'You do not have permission to export accounts.')
        return redirect('employees:account_management')
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="accounts_export.csv"'
    
    writer = csv.writer(response)
    writer.writerow([
        'Name', 'Email', 'Email Password', 'Teams', 'Teams Password', 
        'Basecamp Password', 'System Password', 'GitHub', 'GitHub Password', 
        'Notes', 'Is Active', 'Created At'
    ])
    
    accounts = AccountManagement.objects.all().order_by('name')
    for account in accounts:
        writer.writerow([
            account.name,
            account.email,
            account.email_password,
            account.teams,
            account.teams_password,
            account.basecamp_password,
            account.system_password,
            account.github,
            account.github_password,
            account.notes,
            account.is_active,
            account.created_at.strftime('%Y-%m-%d %H:%M:%S')
        ])
    
    return response


@login_required
def account_sample_csv(request):
    """
    View to download sample CSV template
    """
    if not request.user.is_staff and not request.user.is_superuser:
        messages.error(request, 'You do not have permission to download sample CSV.')
        return redirect('employees:account_management')
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="accounts_sample_template.csv"'
    
    writer = csv.writer(response)
    writer.writerow([
        'Name', 'Email', 'Email Password', 'Teams', 'Teams Password', 
        'Basecamp Password', 'System Password', 'GitHub', 'GitHub Password', 'Notes'
    ])
    
    # Add sample data
    writer.writerow([
        'John Doe', 'john.doe@example.com', 'email_password123', 'john_teams', 'teams123',
        'basecamp123', 'system123', 'johndoe', 'github123', 'Sample account for John Doe'
    ])
    writer.writerow([
        'Jane Smith', 'jane.smith@example.com', 'email_password456', 'jane_teams', 'teams456',
        'basecamp456', 'system456', 'janesmith', 'github456', 'Sample account for Jane Smith'
    ])
    
    return response


@login_required
def account_bulk_delete(request):
    """
    View to bulk delete selected accounts
    """
    if not request.user.is_staff and not request.user.is_superuser:
        messages.error(request, 'You do not have permission to delete accounts.')
        return redirect('employees:account_management')
    
    if request.method == 'POST':
        selected_accounts = request.POST.getlist('selected_accounts')
        
        if not selected_accounts:
            messages.error(request, 'No accounts selected for deletion.')
            return redirect('employees:account_management')
        
        try:
            accounts_to_delete = AccountManagement.objects.filter(id__in=selected_accounts)
            deleted_count = accounts_to_delete.count()
            
            # Get account names for message
            account_names = list(accounts_to_delete.values_list('name', flat=True))
            
            accounts_to_delete.delete()
            
            messages.success(request, f'Successfully deleted {deleted_count} accounts: {", ".join(account_names)}')
            
        except Exception as e:
            messages.error(request, f'Error deleting accounts: {str(e)}')
    
    return redirect('employees:account_management')


@login_required
def account_bulk_export(request):
    """
    View to bulk export selected accounts to CSV
    """
    if not request.user.is_staff and not request.user.is_superuser:
        messages.error(request, 'You do not have permission to export accounts.')
        return redirect('employees:account_management')
    
    if request.method == 'POST':
        selected_accounts = request.POST.getlist('selected_accounts')
        
        if not selected_accounts:
            messages.error(request, 'No accounts selected for export.')
            return redirect('employees:account_management')
        
        try:
            accounts = AccountManagement.objects.filter(id__in=selected_accounts).order_by('name')
            
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="selected_accounts_export.csv"'
            
            writer = csv.writer(response)
            writer.writerow([
                'Name', 'Email', 'Email Password', 'Teams', 'Teams Password', 
                'Basecamp Password', 'System Password', 'GitHub', 'GitHub Password', 
                'Notes', 'Is Active', 'Created At'
            ])
            
            for account in accounts:
                writer.writerow([
                    account.name,
                    account.email,
                    account.email_password,
                    account.teams,
                    account.teams_password,
                    account.basecamp_password,
                    account.system_password,
                    account.github,
                    account.github_password,
                    account.notes,
                    account.is_active,
                    account.created_at.strftime('%Y-%m-%d %H:%M:%S')
                ])
            
            return response
            
        except Exception as e:
            messages.error(request, f'Error exporting accounts: {str(e)}')
    
    return redirect('employees:account_management')
