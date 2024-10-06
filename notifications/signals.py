from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from django.utils import timezone

from liveExam.models import LiveExam
from services.models import Package, UserPackage
from .models import Notification, NotificationPreference
from exams.models import Exam, UserExam
from blog.models import Post
from books.models import Book
from .utils import send_notification

User = get_user_model()

@receiver(post_save, sender=User)
def create_notification_preference(sender, instance, created, **kwargs):
    if created:
        NotificationPreference.objects.create(user=instance)

@receiver(post_save, sender=LiveExam)
def live_exam_notification(sender, instance, created, **kwargs):
    if created and instance.exam_category:
        # Get all active UserPackage instances that include this exam category and are not expired
        user_packages = UserPackage.objects.filter(
            package__exam_categories=instance.exam_category,
            is_active=True,
            expiry_date__gt=timezone.now()
        ).select_related('user')
        
        # Create notifications for users with active packages
        for user_package in user_packages:
            Notification.objects.create(
                user=user_package.user,
                notification_type='live_exam',
                content_object=instance,
                message=f'নতুন লাইভ পরীক্ষা "{instance.title}" যুক্ত করা হয়েছে।'
            )

@receiver(post_save, sender=UserExam)
def exam_result_notification(sender, instance, created, **kwargs):
    if instance.is_completed and not created:
        send_notification(instance.user, 'exam_result', instance, {
            'title': "পরীক্ষার ফলাফল প্রকাশিত",
            'message': f"{instance.exam.title} পরীক্ষার ফলাফল প্রকাশিত হয়েছে। আপনার স্কোর: {instance.score}"
        })

@receiver(post_save, sender=Post)
def blog_post_notification(sender, instance, created, **kwargs):
    if created:
        users_to_notify = NotificationPreference.objects.filter(blog_post=True).values_list('user', flat=True)
        for user_id in users_to_notify:
            send_notification(user_id, 'blog_post', instance, {
                'title': "নতুন ব্লগ পোস্ট",
                'message': f"নতুন ব্লগ পোস্ট প্রকাশিত হয়েছে: {instance.title}"
            })

@receiver(post_save, sender=Book)
def book_purchase_notification(sender, instance, created, **kwargs):
    if instance.is_purchased and not created:
        send_notification(instance.user, 'book_purchase', instance, {
            'title': "বই ক্রয় সম্পন্ন",
            'message': f"আপনি সফলভাবে '{instance.title}' বইটি ক্রয় করেছেন।"
        })

@receiver(post_save, sender=Package)
def package_purchase_notification(sender, instance, created, **kwargs):
    if instance.is_purchased and not created:
        send_notification(instance.user, 'package_purchase', instance, {
            'title': "প্যাকেজ ক্রয় সম্পন্ন",
            'message': f"আপনি সফলভাবে {instance.name} প্যাকেজটি ক্রয় করেছেন।"
        })

def check_upcoming_exams():
    upcoming_exams = Exam.objects.filter(
        exam_date__gte=timezone.now(),
        exam_date__lte=timezone.now() + timezone.timedelta(days=7)
    )
    for exam in upcoming_exams:
        users_to_notify = NotificationPreference.objects.filter(upcoming_exam=True).values_list('user', flat=True)
        for user_id in users_to_notify:
            send_notification(user_id, 'upcoming_exam', exam, {
                'title': "আসন্ন পরীক্ষা",
                'message': f"{exam.title} পরীক্ষাটি {exam.exam_date} তারিখে অনুষ্ঠিত হবে।"
            })
