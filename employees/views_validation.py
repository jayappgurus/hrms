"""

views_validation.py

====================

HRMS Portal — Centralised Backend Validation Utilities  (#12)



All validation helpers live here so they can be reused across

views, forms, and API endpoints without duplication.



Pattern used:

  - Each validator raises django.core.exceptions.ValidationError on failure

  - Calling code wraps validators in try/except ValidationError

  - AJAX views return JSON  {"valid": false, "errors": {...}}

  - Django views add messages.error() and re-render the form

"""



import logging

import re

from datetime import date, datetime

from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.forms import Form, ModelForm
from django.http import JsonResponse

from django.core.exceptions import ValidationError

from django.utils import timezone



logger = logging.getLogger('employees')





# ============================================================

# Generic helpers

# ============================================================



def _require(value, field_name: str):

    """Raise ValidationError if value is empty/None."""

    if value is None or (isinstance(value, str) and not value.strip()):

        raise ValidationError({field_name: f"{field_name.replace('_', ' ').title()} is required."})







# ============================================================

# Employee field validators

# ============================================================



def validate_aadhar(aadhar: str) -> str:

    """

    Validate a 12-digit Aadhar card number.

    Returns cleaned value.

    Raises ValidationError on failure.

    """

    try:

        aadhar = str(aadhar).strip().replace(' ', '')

        if not re.fullmatch(r'\d{12}', aadhar):

            raise ValidationError({'aadhar_card_number': 'Aadhar number must be exactly 12 digits.'})

        return aadhar

    except ValidationError:

        raise

    except Exception as exc:

        logger.error("validate_aadhar unexpected error: %s", exc, exc_info=True)

        raise ValidationError({'aadhar_card_number': 'Invalid Aadhar number.'})







def validate_pan(pan: str) -> str:

    """

    Validate a PAN card number (e.g. ABCDE1234F).

    Returns upper-cased cleaned value.

    Raises ValidationError on failure.

    """

    try:

        pan = str(pan).strip().upper()

        if not re.fullmatch(r'[A-Z]{5}[0-9]{4}[A-Z]{1}', pan):

            raise ValidationError({

                'pan_card_number': 'PAN must match the pattern ABCDE1234F (5 letters, 4 digits, 1 letter).'

            })

        return pan

    except ValidationError:

        raise

    except Exception as exc:

        logger.error("validate_pan unexpected error: %s", exc, exc_info=True)

        raise ValidationError({'pan_card_number': 'Invalid PAN number.'})







def validate_mobile(mobile: str) -> str:

    """

    Validate an Indian mobile number (10 digits, optionally prefixed with +91).

    Returns cleaned value.

    """

    try:

        mobile = str(mobile).strip()

        # Strip leading +91 or 91

        if mobile.startswith('+91'):

            mobile = mobile[3:]

        elif mobile.startswith('91') and len(mobile) == 12:

            mobile = mobile[2:]

        if not re.fullmatch(r'[6-9]\d{9}', mobile):

            raise ValidationError({

                'mobile_number': 'Enter a valid 10-digit Indian mobile number starting with 6-9.'

            })

        return mobile

    except ValidationError:

        raise

    except Exception as exc:

        logger.error("validate_mobile unexpected error: %s", exc, exc_info=True)

        raise ValidationError({'mobile_number': 'Invalid mobile number.'})







def validate_email(email: str, field_name: str = 'email') -> str:

    """Simple email format validation."""

    try:

        email = str(email).strip().lower()

        if not re.fullmatch(r'[^@\s]+@[^@\s]+\.[^@\s]+', email):

            raise ValidationError({field_name: 'Enter a valid email address.'})

        return email

    except ValidationError:

        raise

    except Exception as exc:

        logger.error("validate_email unexpected error: %s", exc, exc_info=True)

        raise ValidationError({field_name: 'Invalid email address.'})







# ============================================================

# Date validators

# ============================================================



def validate_date_not_future(value: date, field_name: str):

    """Raise ValidationError if value is in the future."""

    try:

        today = date.today()

        if value > today:

            raise ValidationError({field_name: f"{field_name.replace('_', ' ').title()} cannot be a future date."})

    except ValidationError:

        raise

    except Exception as exc:

        logger.error("validate_date_not_future error: %s", exc, exc_info=True)

        raise ValidationError({field_name: 'Invalid date.'})







def validate_date_range(start: date, end: date, start_field: str = 'start_date', end_field: str = 'end_date'):

    """Raise ValidationError if end date is before start date."""

    try:

        if start and end and end < start:

            raise ValidationError({end_field: f"End date ({end}) must be on or after start date ({start})."})

    except ValidationError:

        raise

    except Exception as exc:

        logger.error("validate_date_range error: %s", exc, exc_info=True)

        raise





def validate_minimum_age(dob: date, minimum_age: int = 18, field_name: str = 'date_of_birth'):

    """Raise ValidationError if the person is younger than minimum_age."""

    try:

        today = date.today()

        age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))

        if age < minimum_age:

            raise ValidationError({

                field_name: f"Employee must be at least {minimum_age} years old. Current age: {age}."

            })

    except ValidationError:

        raise

    except Exception as exc:

        logger.error("validate_minimum_age error: %s", exc, exc_info=True)

        raise





def validate_joining_date_before_relieving(joining: date, relieving: date):

    """Relieving date must be after joining date."""

    try:

        if joining and relieving and relieving <= joining:

            raise ValidationError({

                'relieving_date': 'Relieving date must be after the joining date.'

            })

    except ValidationError:

        raise

    except Exception as exc:

        logger.error("validate_joining_date_before_relieving error: %s", exc, exc_info=True)

        raise





# ============================================================

# Leave validators

# ============================================================



def validate_leave_dates_not_weekend(start: date, end: date):

    """

    Warn if leave starts or ends on a weekend.

    Raises ValidationError listing the offending dates.

    """

    from .models import PublicHoliday

    try:

        errors = []

        current = start

        while current <= end:

            if current.weekday() in (5, 6):  # Saturday=5, Sunday=6

                errors.append(f"{current.strftime('%d %b %Y')} is a {'Saturday' if current.weekday()==5 else 'Sunday'}.")

            current = date.fromordinal(current.toordinal() + 1)



        if errors:

            raise ValidationError({'start_date': ' '.join(errors) + ' Leave on weekends is not allowed.'})

    except ValidationError:

        raise

    except Exception as exc:

        logger.error("validate_leave_dates_not_weekend error: %s", exc, exc_info=True)

        raise





def validate_leave_not_on_public_holiday(start: date, end: date):

    """

    Raise ValidationError if leave overlaps with a public holiday.

    """

    from .models import PublicHoliday

    try:

        holidays = PublicHoliday.objects.filter(

            date__gte=start, date__lte=end, is_active=True

        ).values_list('date', 'name')



        holiday_list = list(holidays)

        if holiday_list:

            names = ', '.join(f"{h[1]} ({h[0].strftime('%d %b %Y')})" for h in holiday_list)

            raise ValidationError({

                'start_date': f"Leave cannot be applied on public holidays: {names}."

            })

    except ValidationError:

        raise

    except Exception as exc:

        logger.error("validate_leave_not_on_public_holiday error: %s", exc, exc_info=True)

        raise





def validate_employee_leave_balance(employee, leave_type, requested_days: float):

    """

    Check if employee has sufficient leave balance.

    Raises ValidationError if balance is insufficient.

    """

    from .models import LeaveApplication

    try:

        used_days = LeaveApplication.objects.filter(

            employee=employee,

            leave_type=leave_type,

            status='approved',

            start_date__year=timezone.now().year,

        ).aggregate(

            total=models.Sum('total_days')

        )['total'] or 0



        remaining = float(leave_type.max_days_per_year) - float(used_days)

        if requested_days > remaining:

            raise ValidationError({

                'leave_type': (

                    f"Insufficient leave balance. Requested: {requested_days} day(s). "

                    f"Available: {remaining} day(s)."

                )

            })

        return remaining

    except ValidationError:

        raise

    except Exception as exc:

        logger.error(

            "validate_employee_leave_balance error for employee=%s: %s",

            employee.pk, exc, exc_info=True

        )

        raise





# ============================================================

# Device validators

# ============================================================



def validate_device_availability(device):

    """

    Raise ValidationError if the device is not available for allocation.

    """

    try:

        if device.status != 'available':

            raise ValidationError({

                'device': f"Device '{device.device_name}' is not available (status: {device.status})."

            })

    except ValidationError:

        raise

    except Exception as exc:

        logger.error("validate_device_availability error: %s", exc, exc_info=True)

        raise





# ============================================================

# AJAX validation helper

# ============================================================



def collect_validation_errors(validators_with_args: list) -> dict:

    """

    Run multiple validators and collect all errors without stopping at first.



    Usage::

        errors = collect_validation_errors([

            (validate_aadhar, ['123456789012']),

            (validate_pan, ['ABCDE1234F']),

        ])

        if errors:

            return JsonResponse({'valid': False, 'errors': errors}, status=400)



    Returns a dict of {field_name: [error_message, ...]} collected from all validators.

    """

    all_errors = {}

    for validator, args in validators_with_args:

        try:

            validator(*args)

        except ValidationError as exc:

            for field, messages in exc.message_dict.items():

                all_errors.setdefault(field, []).extend(messages)

        except Exception as exc:

            logger.error("collect_validation_errors unexpected: %s", exc, exc_info=True)

            all_errors.setdefault('__all__', []).append(str(exc))

    return all_errors





@csrf_exempt
def validate_employee_form(request):

    """

    AJAX endpoint to validate employee form data.

    Returns JSON with validation results.

    """

    from django.http import JsonResponse

    
    try:

        # Get form data from request

        if request.method == 'POST':

            data = request.POST.dict()

        else:

            data = request.GET.dict()

        

        # Collect validation errors

        errors = {}

        

        # Validate required fields
        required_fields = ['full_name', 'employee_code', 'department', 'designation']

        for field in required_fields:
            if not data.get(field):
                errors[field] = f"{field.replace('_', ' ').title()} is required."

        

        # Validate email format
        if data.get('official_email'):
            import re
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_pattern, data['official_email']):
                errors['official_email'] = 'Please enter a valid official email address.'
        
        if data.get('personal_email'):
            import re
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_pattern, data['personal_email']):
                errors['personal_email'] = 'Please enter a valid personal email address.'

        

        # Validate phone number
        if data.get('mobile_number'):
            phone = re.sub(r'[^\d]', '', data['mobile_number'])
            if len(phone) != 10:
                errors['mobile_number'] = 'Mobile number must be 10 digits.'

        

        # Return validation result

        if errors:

            return JsonResponse({'valid': False, 'errors': errors})

        else:

            return JsonResponse({'valid': True, 'message': 'Validation successful'})

            

    except Exception as e:

        logger.error(f"Employee form validation error: {str(e)}", exc_info=True)

        return JsonResponse({

            'valid': False, 

            'errors': {'__all__': 'Validation error occurred'}

        })







def validate_leave_application_form(request):

    """

    AJAX endpoint to validate leave application form data.

    Returns JSON with validation results.

    """

    from django.http import JsonResponse

    
    try:

        # Get form data from request

        if request.method == 'POST':

            data = request.POST.dict()

        else:

            data = request.GET.dict()

        

        # Collect validation errors

        errors = {}

        

        # Validate required fields

        required_fields = ['leave_type', 'start_date', 'end_date']

        for field in required_fields:

            if not data.get(field):

                errors[field] = f"{field.replace('_', ' ').title()} is required."

        

        # Validate date logic

        if data.get('start_date') and data.get('end_date'):

            try:

                from datetime import datetime

                start_date = datetime.strptime(data['start_date'], '%Y-%m-%d')

                end_date = datetime.strptime(data['end_date'], '%Y-%m-%d')

                

                if start_date > end_date:

                    errors['end_date'] = 'End date must be after start date.'

            except ValueError:

                errors['date'] = 'Invalid date format.'

        

        # Return validation result

        if errors:

            return JsonResponse({'valid': False, 'errors': errors})

        else:

            return JsonResponse({'valid': True, 'message': 'Validation successful'})

            

    except Exception as e:

        logger.error(f"Leave application validation error: {str(e)}", exc_info=True)

        return JsonResponse({

            'valid': False, 

            'errors': {'__all__': 'Validation error occurred'}

        })







def validate_public_holiday_form(request):

    """

    AJAX endpoint to validate public holiday form data.

    Returns JSON with validation results.

    """

    from django.http import JsonResponse

    
    try:

        # Get form data from request

        if request.method == 'POST':

            data = request.POST.dict()

        else:

            data = request.GET.dict()

        

        # Collect validation errors

        errors = {}

        

        # Validate required fields

        required_fields = ['name', 'date']

        for field in required_fields:

            if not data.get(field):

                errors[field] = f"{field.replace('_', ' ').title()} is required."

        

        # Validate date format

        if data.get('date'):

            try:

                from datetime import datetime

                datetime.strptime(data['date'], '%Y-%m-%d')

            except ValueError:

                errors['date'] = 'Invalid date format. Use YYYY-MM-DD.'

        

        # Return validation result

        if errors:

            return JsonResponse({'valid': False, 'errors': errors})

        else:

            return JsonResponse({'valid': True, 'message': 'Validation successful'})

            

    except Exception as e:

        logger.error(f"Public holiday validation error: {str(e)}", exc_info=True)

        return JsonResponse({

            'valid': False, 

            'errors': {'__all__': 'Validation error occurred'}

        })







def validate_leave_type_form(request):

    """

    AJAX endpoint to validate leave type form data.

    Returns JSON with validation results.

    """

    from django.http import JsonResponse

    
    try:

        # Get form data from request

        if request.method == 'POST':

            data = request.POST.dict()

        else:

            data = request.GET.dict()

        

        # Collect validation errors

        errors = {}

        

        # Validate required fields

        required_fields = ['name', 'days_allowed']

        for field in required_fields:

            if not data.get(field):

                errors[field] = f"{field.replace('_', ' ').title()} is required."

        

        # Validate days allowed

        if data.get('days_allowed'):

            try:

                days = int(data['days_allowed'])

                if days <= 0:

                    errors['days_allowed'] = 'Days allowed must be greater than 0.'

            except ValueError:

                errors['days_allowed'] = 'Invalid number format.'

        

        # Return validation result

        if errors:

            return JsonResponse({'valid': False, 'errors': errors})

        else:

            return JsonResponse({'valid': True, 'message': 'Validation successful'})

            

    except Exception as e:

        logger.error(f"Leave type validation error: {str(e)}", exc_info=True)

        return JsonResponse({

            'valid': False, 

            'errors': {'__all__': 'Validation error occurred'}

        })





def validate_device_request_form(request):
    """
    AJAX endpoint to validate device request form data.
    Returns JSON with validation results.
    """
    from django.http import JsonResponse
    
    try:
        # Get form data from request
        if request.method == 'POST':
            data = request.POST.dict()
        else:
            data = request.GET.dict()
        
        # Collect validation errors
        errors = {}
        
        # Validate required fields
        required_fields = ['device', 'employee', 'request_date']
        for field in required_fields:
            if not data.get(field):
                errors[field] = f"{field.replace('_', ' ').title()} is required."
        
        # Validate date format
        if data.get('request_date'):
            try:
                from datetime import datetime
                datetime.strptime(data['request_date'], '%Y-%m-%d')
            except ValueError:
                errors['request_date'] = 'Invalid date format. Use YYYY-MM-DD.'
        
        # Validate device availability if device ID is provided
        if data.get('device'):
            try:
                from .models import Device
                device = Device.objects.get(pk=data['device'])
                validate_device_availability(device)
            except Device.DoesNotExist:
                errors['device'] = 'Selected device does not exist.'
            except ValidationError as e:
                errors.update(e.message_dict)
        
        # Return validation result
        if errors:
            return JsonResponse({'valid': False, 'errors': errors})
        else:
            return JsonResponse({'valid': True, 'message': 'Validation successful'})
            
    except Exception as e:
        logger.error(f"Device request validation error: {str(e)}", exc_info=True)
        return JsonResponse({
            'valid': False, 
            'errors': {'__all__': 'Validation error occurred'}
        })



def validate_account_management_form(request):
    """
    AJAX endpoint to validate account management form data.
    Returns JSON with validation results.
    """
    from django.http import JsonResponse
    
    try:
        # Get form data from request
        if request.method == 'POST':
            data = request.POST.dict()
        else:
            data = request.GET.dict()
        
        # Collect validation errors
        errors = {}
        
        # Validate required fields
        required_fields = ['username', 'email', 'role']
        for field in required_fields:
            if not data.get(field):
                errors[field] = f"{field.replace('_', ' ').title()} is required."
        
        # Validate email format
        if data.get('email'):
            import re
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_pattern, data['email']):
                errors['email'] = 'Please enter a valid email address.'
        
        # Return validation result
        if errors:
            return JsonResponse({'valid': False, 'errors': errors})
        else:
            return JsonResponse({'valid': True, 'message': 'Validation successful'})
            
    except Exception as e:
        logger.error(f"Account management validation error: {str(e)}", exc_info=True)
        return JsonResponse({
            'valid': False, 
            'errors': {'__all__': 'Validation error occurred'}
        })



def validate_job_description_form(request):
    """
    AJAX endpoint to validate job description form data.
    Returns JSON with validation results.
    """
    from django.http import JsonResponse
    
    try:
        # Get form data from request
        if request.method == 'POST':
            data = request.POST.dict()
        else:
            data = request.GET.dict()
        
        # Collect validation errors
        errors = {}
        
        # Validate required fields
        required_fields = ['title', 'department', 'description']
        for field in required_fields:
            if not data.get(field):
                errors[field] = f"{field.replace('_', ' ').title()} is required."
        
        # Return validation result
        if errors:
            return JsonResponse({'valid': False, 'errors': errors})
        else:
            return JsonResponse({'valid': True, 'message': 'Validation successful'})
            
    except Exception as e:
        logger.error(f"Job description validation error: {str(e)}", exc_info=True)
        return JsonResponse({
            'valid': False, 
            'errors': {'__all__': 'Validation error occurred'}
        })



def validate_job_application_form(request):
    """
    AJAX endpoint to validate job application form data.
    Returns JSON with validation results.
    """
    from django.http import JsonResponse
    
    try:
        # Get form data from request
        if request.method == 'POST':
            data = request.POST.dict()
        else:
            data = request.GET.dict()
        
        # Collect validation errors
        errors = {}
        
        # Validate required fields
        required_fields = ['applicant_name', 'email', 'job']
        for field in required_fields:
            if not data.get(field):
                errors[field] = f"{field.replace('_', ' ').title()} is required."
        
        # Validate email format
        if data.get('email'):
            import re
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_pattern, data['email']):
                errors['email'] = 'Please enter a valid email address.'
        
        # Return validation result
        if errors:
            return JsonResponse({'valid': False, 'errors': errors})
        else:
            return JsonResponse({'valid': True, 'message': 'Validation successful'})
            
    except Exception as e:
        logger.error(f"Job application validation error: {str(e)}", exc_info=True)
        return JsonResponse({
            'valid': False, 
            'errors': {'__all__': 'Validation error occurred'}
        })



def validate_interview_schedule_form(request):
    """
    AJAX endpoint to validate interview schedule form data.
    Returns JSON with validation results.
    """
    from django.http import JsonResponse
    
    try:
        # Get form data from request
        if request.method == 'POST':
            data = request.POST.dict()
        else:
            data = request.GET.dict()
        
        # Collect validation errors
        errors = {}
        
        # Validate required fields
        required_fields = ['candidate', 'job', 'interview_date', 'interview_time']
        for field in required_fields:
            if not data.get(field):
                errors[field] = f"{field.replace('_', ' ').title()} is required."
        
        # Validate date format
        if data.get('interview_date'):
            try:
                from datetime import datetime
                datetime.strptime(data['interview_date'], '%Y-%m-%d')
            except ValueError:
                errors['interview_date'] = 'Invalid date format. Use YYYY-MM-DD.'
        
        # Return validation result
        if errors:
            return JsonResponse({'valid': False, 'errors': errors})
        else:
            return JsonResponse({'valid': True, 'message': 'Validation successful'})
            
    except Exception as e:
        logger.error(f"Interview schedule validation error: {str(e)}", exc_info=True)
        return JsonResponse({
            'valid': False, 
            'errors': {'__all__': 'Validation error occurred'}
        })



@csrf_exempt
@require_POST
@login_required
def validate_system_detail_form(request):
    """
    AJAX endpoint to validate system detail form data.
    Returns JSON with validation results.
    """
    from django.http import JsonResponse
    
    try:
        # Get form data from request
        if request.method == 'POST':
            data = request.POST.dict()
        else:
            data = request.GET.dict()
        
        # Collect validation errors
        errors = {}
        
        # Validate required fields
        required_fields = ['system_name', 'system_type']
        for field in required_fields:
            if not data.get(field):
                errors[field] = f"{field.replace('_', ' ').title()} is required."
        
        # Return validation result
        if errors:
            return JsonResponse({'valid': False, 'errors': errors})
        else:
            return JsonResponse({'valid': True, 'message': 'Validation successful'})
            
    except Exception as e:
        logger.error(f"System detail validation error: {str(e)}", exc_info=True)
        return JsonResponse({
            'valid': False, 
            'errors': {'__all__': 'Validation error occurred'}
        })



def validate_system_requirement_form(request):
    """
    AJAX endpoint to validate system requirement form data.
    Returns JSON with validation results.
    """
    from django.http import JsonResponse
    
    try:
        # Get form data from request
        if request.method == 'POST':
            data = request.POST.dict()
        else:
            data = request.GET.dict()
        
        # Collect validation errors
        errors = {}
        
        # Validate required fields
        required_fields = ['requirement_name', 'description']
        for field in required_fields:
            if not data.get(field):
                errors[field] = f"{field.replace('_', ' ').title()} is required."
        
        # Return validation result
        if errors:
            return JsonResponse({'valid': False, 'errors': errors})
        else:
            return JsonResponse({'valid': True, 'message': 'Validation successful'})
            
    except Exception as e:
        logger.error(f"System requirement validation error: {str(e)}", exc_info=True)
        return JsonResponse({
            'valid': False, 
            'errors': {'__all__': 'Validation error occurred'}
        })



def validate_user_create_form(request):
    """
    AJAX endpoint to validate user create form data.
    Returns JSON with validation results.
    """
    from django.http import JsonResponse
    
    try:
        # Get form data from request
        if request.method == 'POST':
            data = request.POST.dict()
        else:
            data = request.GET.dict()
        
        # Collect validation errors
        errors = {}
        
        # Validate required fields
        required_fields = ['username', 'email', 'password']
        for field in required_fields:
            if not data.get(field):
                errors[field] = f"{field.replace('_', ' ').title()} is required."
        
        # Validate email format
        if data.get('email'):
            import re
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_pattern, data['email']):
                errors['email'] = 'Please enter a valid email address.'
        
        # Validate password length
        if data.get('password') and len(data['password']) < 8:
            errors['password'] = 'Password must be at least 8 characters long.'
        
        # Return validation result
        if errors:
            return JsonResponse({'valid': False, 'errors': errors})
        else:
            return JsonResponse({'valid': True, 'message': 'Validation successful'})
            
    except Exception as e:
        logger.error(f"User create validation error: {str(e)}", exc_info=True)
        return JsonResponse({
            'valid': False, 
            'errors': {'__all__': 'Validation error occurred'}
        })



def validate_user_profile_form(request):
    """
    AJAX endpoint to validate user profile form data.
    Returns JSON with validation results.
    """
    from django.http import JsonResponse
    
    try:
        # Get form data from request
        if request.method == 'POST':
            data = request.POST.dict()
        else:
            data = request.GET.dict()
        
        # Collect validation errors
        errors = {}
        
        # Validate required fields
        required_fields = ['first_name', 'last_name', 'email']
        for field in required_fields:
            if not data.get(field):
                errors[field] = f"{field.replace('_', ' ').title()} is required."
        
        # Validate email format
        if data.get('email'):
            import re
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_pattern, data['email']):
                errors['email'] = 'Please enter a valid email address.'
        
        # Return validation result
        if errors:
            return JsonResponse({'valid': False, 'errors': errors})
        else:
            return JsonResponse({'valid': True, 'message': 'Validation successful'})
            
    except Exception as e:
        logger.error(f"User profile validation error: {str(e)}", exc_info=True)
        return JsonResponse({
            'valid': False, 
            'errors': {'__all__': 'Validation error occurred'}
        })


def check_leave_dates(request):
    """
    AJAX endpoint to check if selected dates include weekends or public holidays.
    Returns JSON with validation results.
    """
    from django.http import JsonResponse
    from datetime import datetime, timedelta
    from .leave_service import LeaveManagementService
    from .models import PublicHoliday
    
    try:
        start_date_str = request.GET.get('start_date')
        end_date_str = request.GET.get('end_date')
        
        if not start_date_str or not end_date_str:
            return JsonResponse({
                'valid': True,
                'message': ''
            })
        
        # Parse dates
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
        except ValueError:
            return JsonResponse({
                'valid': False,
                'message': 'Invalid date format'
            })
        
        # Check if end date is before start date
        if end_date < start_date:
            return JsonResponse({
                'valid': False,
                'message': 'End date must be after or equal to start date'
            })
        
        # Check for weekends and holidays
        invalid_dates = []
        current_date = start_date
        
        while current_date <= end_date:
            # Check if weekend
            if LeaveManagementService.is_weekend(current_date):
                day_name = current_date.strftime('%A')
                date_str = current_date.strftime('%d-%m-%Y')
                invalid_dates.append(f"{day_name}, {date_str} (Weekend)")
            
            # Check if public holiday
            elif LeaveManagementService.is_public_holiday(current_date, country='IN'):
                holiday = PublicHoliday.objects.filter(
                    date=current_date,
                    country='IN',
                    is_active=True
                ).first()
                date_str = current_date.strftime('%d-%m-%Y')
                holiday_name = holiday.name if holiday else "Public Holiday"
                invalid_dates.append(f"{date_str} ({holiday_name})")
            
            current_date += timedelta(days=1)
        
        if invalid_dates:
            if len(invalid_dates) == 1:
                message = f"❌ Cannot apply leave: {invalid_dates[0]} is a non-working day. Please select working days only (Monday to Friday, excluding public holidays)."
            else:
                dates_list = ", ".join(invalid_dates[:3])
                if len(invalid_dates) > 3:
                    dates_list += f" and {len(invalid_dates) - 3} more"
                message = f"❌ Cannot apply leave: The selected range includes non-working days: {dates_list}. Please select working days only."
            
            return JsonResponse({
                'valid': False,
                'message': message,
                'invalid_dates': invalid_dates
            })
        
        # All dates are valid working days
        working_days = LeaveManagementService.count_working_days(start_date, end_date, country='IN')
        return JsonResponse({
            'valid': True,
            'message': f'✓ Valid working days selected ({working_days} day{"s" if working_days != 1 else ""})',
            'working_days': working_days
        })
        
    except Exception as e:
        return JsonResponse({
            'valid': False,
            'message': f'Error validating dates: {str(e)}'
        })
