from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import Device


@login_required
def api_available_devices(request, device_type):
    """API endpoint to get available devices by type"""
    if not request.user.is_superuser and not request.user.is_staff:
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    try:
        devices = Device.objects.filter(
            device_type=device_type,
            status='available'
        ).values('id', 'device_name', 'serial_number')
        
        return JsonResponse({
            'devices': list(devices)
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
