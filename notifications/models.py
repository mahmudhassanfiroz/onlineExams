from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

from accounts.models import CustomUser
from django_ckeditor_5.fields import CKEditor5Field
class Notification(models.Model):
    NOTIFICATION_TYPES = (
        ('live_exam', 'লাইভ পরীক্ষা'),
        ('exam_schedule', 'পরীক্ষার সময়সূচি'),
        ('exam_result', 'পরীক্ষার ফলাফল'),
        ('blog_post', 'ব্লগ পোস্ট'),
        ('exam_registration', 'পরীক্ষা রেজিস্ট্রেশন'),
        ('book_purchase', 'বই ক্রয়'),
        ('general_info', 'সাধারণ তথ্য'),
    )

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    title = CKEditor5Field(max_length=255)
    message = CKEditor5Field()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey('content_type', 'object_id')

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.get_notification_type_display()} for {self.user.username}"

