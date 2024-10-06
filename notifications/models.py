from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.utils.html import strip_tags

from accounts.models import CustomUser
from django_ckeditor_5.fields import CKEditor5Field

class Notification(models.Model):
    NOTIFICATION_TYPES = (
        ('live_exam', 'লাইভ পরীক্ষা'),
        ('exam_result', 'পরীক্ষার ফলাফল'),
        ('blog_post', 'ব্লগ পোস্ট'),
        ('book_purchase', 'বই ক্রয়'),
        ('general_info', 'সাধারণ তথ্য'),
        ('upcoming_exam', 'আসন্ন পরীক্ষা'),
        ('login', 'লগইন'),
        ('package_purchase', 'প্যাকেজ ক্রয়'),
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

    def get_stripped_title(self):
        return strip_tags(self.title)

    def get_stripped_message(self):
        return strip_tags(self.message)

    @classmethod
    def get_unread_count(cls, user):
        return cls.objects.filter(user=user, is_read=False).count()

    def mark_as_read(self):
        self.is_read = True
        self.save()

    @classmethod
    def create_live_exam_notification(cls, user, live_exam):
        title = "লাইভ পরীক্ষা"
        message = f"{live_exam.title} লাইভ পরীক্ষাটি {live_exam.exam_date} তারিখে অনুষ্ঠিত হবে।"
        return cls.objects.create(
            user=user,
            notification_type='live_exam',
            title=title,
            message=message,
            content_object=live_exam
        )

    @classmethod
    def create_exam_result_notification(cls, user, user_exam):
        title = "পরীক্ষার ফলাফল প্রকাশিত হয়েছে"
        message = f"{user_exam.exam.title} পরীক্ষার ফলাফল প্রকাশিত হয়েছে। আপনার স্কোর: {user_exam.score}"
        return cls.objects.create(
            user=user,
            notification_type='exam_result',
            title=title,
            message=message,
            content_object=user_exam
        )

    @classmethod
    def create_blog_post_notification(cls, user, blog_post):
        title = "নতুন ব্লগ পোস্ট"
        message = f"নতুন ব্লগ পোস্ট প্রকাশিত হয়েছে: {blog_post.title}"
        return cls.objects.create(
            user=user,
            notification_type='blog_post',
            title=title,
            message=message,
            content_object=blog_post
        )

    @classmethod
    def create_book_purchase_notification(cls, user, book):
        title = "বই ক্রয় সম্পন্ন"
        message = f"আপনি সফলভাবে '{book.title}' বইটি ক্রয় করেছেন।"
        return cls.objects.create(
            user=user,
            notification_type='book_purchase',
            title=title,
            message=message,
            content_object=book
        )

    @classmethod
    def create_general_info_notification(cls, user, info):
        title = "সাধারণ তথ্য"
        message = info
        return cls.objects.create(
            user=user,
            notification_type='general_info',
            title=title,
            message=message
        )

    @classmethod
    def create_upcoming_exam_notification(cls, user, exam):
        title = "আসন্ন পরীক্ষা"
        message = f"{exam.title} পরীক্ষাটি {exam.exam_date} তারিখে অনুষ্ঠিত হবে।"
        return cls.objects.create(
            user=user,
            notification_type='upcoming_exam',
            title=title,
            message=message,
            content_object=exam
        )

    @classmethod
    def create_login_notification(cls, user):
        title = "সফল লগইন"
        message = f"আপনি সফলভাবে লগইন করেছেন। স্বাগতম, {user.username}!"
        return cls.objects.create(
            user=user,
            notification_type='login',
            title=title,
            message=message
        )

    @classmethod
    def create_package_purchase_notification(cls, user, package):
        title = "প্যাকেজ ক্রয় সম্পন্ন"
        message = f"আপনি সফলভাবে {package.name} প্যাকেজটি ক্রয় করেছেন।"
        return cls.objects.create(
            user=user,
            notification_type='package_purchase',
            title=title,
            message=message,
            content_object=package
        )

class NotificationPreference(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='notification_preference')
    live_exam = models.BooleanField(default=True)
    exam_result = models.BooleanField(default=True)
    blog_post = models.BooleanField(default=True)
    book_purchase = models.BooleanField(default=True)
    general_info = models.BooleanField(default=True)
    upcoming_exam = models.BooleanField(default=True)
    login = models.BooleanField(default=True)
    package_purchase = models.BooleanField(default=True)

    def __str__(self):
        return f"Notification Preference for {self.user.username}"

class NotificationDevice(models.Model):
    DEVICE_TYPES = (
        ('web', 'ওয়েব'),
        ('android', 'অ্যান্ড্রয়েড'),
        ('ios', 'আইওএস'),
    )
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='notification_devices')
    device_type = models.CharField(max_length=10, choices=DEVICE_TYPES)
    device_token = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.get_device_type_display()} device for {self.user.username}"

class NotificationLog(models.Model):
    notification = models.ForeignKey(Notification, on_delete=models.CASCADE, related_name='logs')
    sent_at = models.DateTimeField(auto_now_add=True)
    is_delivered = models.BooleanField(default=False)
    delivered_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Log for {self.notification}"

