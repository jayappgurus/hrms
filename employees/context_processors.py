from django.db import models
from .models import Notification, Message, NotificationRead, MessageRead

def notifications_and_messages(request):
    """Add unread notifications and messages count to all templates"""
    if request.user.is_authenticated:
        # Get notifications for this user
        if request.user.is_staff or request.user.is_superuser:
            # Staff see all notifications
            all_notifications = Notification.objects.filter(is_active=True)
        else:
            # Regular users see targeted notifications
            all_notifications = Notification.objects.filter(
                is_active=True
            ).filter(
                models.Q(target_all=True) | models.Q(target_users=request.user)
            )

        # Get unread notifications
        read_notification_ids = NotificationRead.objects.filter(
            user=request.user
        ).values_list('notification_id', flat=True)

        unread_notifications = all_notifications.exclude(
            id__in=read_notification_ids
        )[:5]  # Limit to 5 recent

        # Get messages for this user
        if request.user.is_staff or request.user.is_superuser:
            all_messages = Message.objects.all()
        else:
            all_messages = Message.objects.filter(
                models.Q(target_all=True) | models.Q(target_users=request.user)
            )

        # Get unread messages
        read_message_ids = MessageRead.objects.filter(
            user=request.user
        ).values_list('message_id', flat=True)

        unread_messages = all_messages.exclude(
            id__in=read_message_ids
        )[:5]  # Limit to 5 recent

        return {
            'unread_notifications': unread_notifications,
            'unread_notifications_count': unread_notifications.count(),
            'unread_messages': unread_messages,
            'unread_messages_count': unread_messages.count(),
        }

    return {
        'unread_notifications': [],
        'unread_notifications_count': 0,
        'unread_messages': [],
        'unread_messages_count': 0,
    }
