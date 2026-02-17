from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .models import Notification, Message
from .forms_notifications import NotificationForm, MessageForm

def is_staff_or_superuser(user):
    return user.is_staff or user.is_superuser

@login_required
@user_passes_test(is_staff_or_superuser)
def create_notification(request):
    """Create a new notification"""
    if request.method == 'POST':
        form = NotificationForm(request.POST)
        if form.is_valid():
            notification = form.save(commit=False)
            notification.created_by = request.user
            notification.save()
            form.save_m2m()  # Save many-to-many relationships
            messages.success(request, 'Notification created successfully!')
            return redirect('employees:create_notification')
    else:
        form = NotificationForm()

    # Get recent notifications
    recent_notifications = Notification.objects.filter(
        created_by=request.user
    ).order_by('-created_at')[:10]

    context = {
        'form': form,
        'recent_notifications': recent_notifications,
    }
    return render(request, 'notifications/create_notification.html', context)

@login_required
@user_passes_test(is_staff_or_superuser)
def create_message(request):
    """Create a new message"""
    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.sender = request.user
            message.save()
            form.save_m2m()  # Save many-to-many relationships
            messages.success(request, 'Message sent successfully!')
            return redirect('employees:create_message')
    else:
        form = MessageForm()

    # Get recent messages
    recent_messages = Message.objects.filter(
        sender=request.user
    ).order_by('-created_at')[:10]

    context = {
        'form': form,
        'recent_messages': recent_messages,
    }
    return render(request, 'notifications/create_message.html', context)
