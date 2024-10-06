from .models import Notification, NotificationPreference

def send_notification(user, notification_type, content_object=None, extra_data=None):
    if hasattr(user, 'notification_preference'):
        preference = user.notification_preference
        if getattr(preference, notification_type, True):
            notification = Notification.objects.create(
                user=user,
                notification_type=notification_type,
                content_object=content_object,
                title=extra_data.get('title', ''),
                message=extra_data.get('message', '')
            )
            # Here you can add code to send real-time notification
            # For example, using channels to send WebSocket message
            from .consumers import NotificationConsumer
            NotificationConsumer.send_notification_to_user(user.id, notification)
            return notification
    return None

def send_general_info(message, users=None):
    users = users or NotificationPreference.objects.filter(general_info=True).values_list('user', flat=True)
    for user_id in users:
        send_notification(user_id, 'general_info', None, {
            'title': "সাধারণ তথ্য",
            'message': message
        })
