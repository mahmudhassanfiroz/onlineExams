from django.shortcuts import get_object_or_404, redirect
from accounts.models import CustomUser
from .models import Notification
from exams.models import ExamCategory
from notifications.utils import send_notification
from django.shortcuts import render
from django.contrib.auth.decorators import login_required



def schedule_exam(request, exam_id):
    exam = get_object_or_404(ExamCategory, id=exam_id)
    # পরীক্ষা শিডিউল করার লজিক...
    for user in CustomUser.objects.filter(is_active=True):
        send_notification(
            user,
            'exam_schedule',
            f'নতুন পরীক্ষা: {exam.name}',
            f'{exam.name} পরীক্ষাটি {exam.date} তারিখে অনুষ্ঠিত হবে।',
            exam
        )

def publish_result(request, exam_id):
    exam = get_object_or_404(ExamCategory, id=exam_id)
    # ফলাফল প্রকাশের লজিক...
    for participant in exam.participants.all():
        send_notification(
            participant.user,
            'exam_result',
            f'ফলাফল প্রকাশিত: {exam.name}',
            f'{exam.name} পরীক্ষার ফলাফল প্রকাশিত হয়েছে। আপনার ফলাফল দেখতে লগ ইন করুন।',
            exam
        )

@login_required
def notification_list(request):
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'notifications/notification_list.html', {'notifications': notifications})

@login_required
def mark_as_read(request, notification_id):
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    notification.is_read = True
    notification.save()
    return redirect('notifications:notification_list')

