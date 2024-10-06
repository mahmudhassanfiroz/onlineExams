import base64
import io
from django.shortcuts import render, redirect
from django.db.models import Avg, Sum, Count, Q
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from matplotlib import pyplot as plt
from django.utils import timezone
from accounts.models import CustomUser
from notifications.models import Notification
from .models import UserActivity, UserPreference, UserBadge, Feedback, UserProfile
from liveExam.models import LiveExam, UserLiveExam
from results.models import Result
from exams.models import UserExam
from django.contrib.contenttypes.models import ContentType

@login_required
def user_dashboard(request):
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)
    upcoming_exams = LiveExam.objects.filter(start_time__gt=timezone.now()).order_by('start_time')[:5]
    recent_results = Result.objects.filter(
        Q(content_type=ContentType.objects.get_for_model(UserLiveExam), object_id__in=UserLiveExam.objects.filter(user=request.user).values_list('id', flat=True)) |
        Q(content_type=ContentType.objects.get_for_model(UserExam), object_id__in=UserExam.objects.filter(user=request.user).values_list('id', flat=True))
    ).order_by('-submission_time')[:5]
    notifications = Notification.objects.filter(user=request.user, is_read=False)[:5]
    recent_activities = UserActivity.objects.filter(user=request.user).order_by('-created_at')[:10]

    # Performance Metrics
    user_live_exam_content_type = ContentType.objects.get_for_model(UserLiveExam)
    user_exam_content_type = ContentType.objects.get_for_model(UserExam)

    user_results = Result.objects.filter(
        Q(content_type=user_live_exam_content_type, object_id__in=UserLiveExam.objects.filter(user=request.user).values_list('id', flat=True)) |
        Q(content_type=user_exam_content_type, object_id__in=UserExam.objects.filter(user=request.user).values_list('id', flat=True))
    )
    total_exams = Result.objects.filter(
        Q(content_type=user_live_exam_content_type, object_id__in=UserLiveExam.objects.filter(user=request.user).values_list('id', flat=True)) |
        Q(content_type=user_exam_content_type, object_id__in=UserExam.objects.filter(user=request.user).values_list('id', flat=True))
    ).count()
    avg_score = user_results.aggregate(Avg('score'))['score__avg'] or 0
    correct_answers = user_results.aggregate(Sum('correct_answers'))['correct_answers__sum'] or 0
    wrong_answers = user_results.aggregate(Sum('wrong_answers'))['wrong_answers__sum'] or 0

    context = {
        'user_profile': user_profile,
        'upcoming_exams': upcoming_exams,
        'recent_results': recent_results,
        'notifications': notifications,
        'recent_activities': recent_activities,
        'total_exams': total_exams,
        'avg_score': avg_score,
        'correct_answers': correct_answers,
        'wrong_answers': wrong_answers,
    }
    return render(request, 'dashboard/dashboard.html', context)

@login_required
def performance_analysis(request):
    user_live_exam_content_type = ContentType.objects.get_for_model(UserLiveExam)
    user_exam_content_type = ContentType.objects.get_for_model(UserExam)

    print(f"Debug: User ID = {request.user.id}")
    print(f"Debug: UserLiveExam ContentType ID = {user_live_exam_content_type.id}")
    print(f"Debug: UserExam ContentType ID = {user_exam_content_type.id}")

    results = Result.objects.filter(
        Q(
            content_type=user_live_exam_content_type,
            object_id__in=UserLiveExam.objects.filter(user=request.user).values_list('id', flat=True)
        ) |
        Q(
            content_type=user_exam_content_type,
            object_id__in=UserExam.objects.filter(user=request.user).values_list('id', flat=True)
        )
    ).order_by('submission_time')

    print(f"Debug: Query = {results.query}")
    print(f"Debug: Results count = {results.count()}")

    if not results.exists():
        messages.info(request, _('আপনার এখনও কোনও পরীক্ষার ফলাফল নেই।'))
        return redirect('dashboard:user_dashboard')

    scores = [result.score for result in results]
    dates = [result.submission_time for result in results]

    plt.figure(figsize=(10, 5))
    plt.plot(dates, scores, marker='o')
    plt.title(_('পারফরম্যান্স গ্রাফ'))
    plt.xlabel(_('তারিখ'))
    plt.ylabel(_('স্কোর'))
    plt.xticks(rotation=45)
    plt.tight_layout()

    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    image_png = buffer.getvalue()
    buffer.close()

    graphic = base64.b64encode(image_png)
    graphic = graphic.decode('utf-8')

    context = {
        'graphic': graphic,
        'results': results,  # এটি যোগ করুন যাতে টেমপ্লেটে আরও তথ্য দেখানো যায়
    }
    return render(request, 'dashboard/performance_metrics.html', context)

@login_required
def customize_dashboard(request):
    user_preference, created = UserPreference.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        layout = request.POST.get('layout')
        user_preference.dashboard_layout = layout
        user_preference.save()
        messages.success(request, _('ড্যাশবোর্ড লেআউট সফলভাবে আপডেট করা হয়েছে।'))
        return redirect('dashboard:user_dashboard')
    
    context = {'current_layout': user_preference.dashboard_layout}
    return render(request, 'dashboard/customize_dashboard.html', context)

@login_required
def submit_feedback(request):
    if request.method == 'POST':
        message = request.POST.get('message')
        if message:
            Feedback.objects.create(user=request.user, message=message)
            messages.success(request, _('আপনার প্রতিক্রিয়া সফলভাবে জমা দেওয়া হয়েছে। ধন্যবাদ!'))
            return redirect('dashboard:dashboard')
        else:
            messages.error(request, _('দয়া করে একটি বার্তা লিখুন।'))
    return render(request, 'dashboard/submit_feedback.html')

