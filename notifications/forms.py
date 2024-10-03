
from django import forms
from .models import NotificationPreference

class NotificationPreferenceForm(forms.ModelForm):
    class Meta:
        model = NotificationPreference
        fields = ['notification_method', 'email_notifications', 'sms_notifications', 'app_notifications']

