from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import Notification

def send_notification(user, notification_type, title, message, related_object=None):
    notification = Notification.objects.create(
        user=user,
        notification_type=notification_type,
        title=title,
        message=message,
        content_object=related_object
    )
    
    # রিয়েল-টাইম নোটিফিকেশন পাঠান
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f"user_{user.id}_notifications",
        {
            "type": "send_notification",
            "notification": {
                "id": notification.id,
                "type": notification_type,
                "title": title,
                "message": message,
            }
        }
    )
    
    return notification

