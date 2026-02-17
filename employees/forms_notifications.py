from django import forms
from .models import Notification, Message
from django.contrib.auth.models import User

class NotificationForm(forms.ModelForm):
    class Meta:
        model = Notification
        fields = ['title', 'message', 'notification_type', 'icon', 'target_all', 'target_users']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter notification title'
            }),
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Enter notification message'
            }),
            'notification_type': forms.Select(attrs={
                'class': 'form-control'
            }),
            'icon': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., bi-info-circle, bi-check-circle'
            }),
            'target_all': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'target_users': forms.SelectMultiple(attrs={
                'class': 'form-control',
                'size': '10'
            }),
        }
        labels = {
            'title': 'Notification Title',
            'message': 'Message',
            'notification_type': 'Type',
            'icon': 'Icon (Bootstrap Icon class)',
            'target_all': 'Send to All Employees',
            'target_users': 'Or Select Specific Users',
        }

class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['subject', 'body', 'target_all', 'target_users']
        widgets = {
            'subject': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter message subject'
            }),
            'body': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 6,
                'placeholder': 'Enter message body'
            }),
            'target_all': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'target_users': forms.SelectMultiple(attrs={
                'class': 'form-control',
                'size': '10'
            }),
        }
        labels = {
            'subject': 'Subject',
            'body': 'Message Body',
            'target_all': 'Send to All Employees',
            'target_users': 'Or Select Specific Users',
        }
