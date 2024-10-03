import base64
import io
from django.shortcuts import render, redirect
from django.db.models import Avg, Sum, Count
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from matplotlib import pyplot as plt
from django.utils import timezone
from accounts.models import CustomUser
from notifications.models import Notification
from exams.models import ExamRegistration
from services.views import get_active_promotions
from services.models import Review, ServiceRegistration
from .models import UserActivity, UserPreference, UserBadge, Feedback, UserProfile
from liveExam.models import LiveExam
from results.models import Result

@login_required
def user_dashboard(request):
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)
    upcoming_exams = LiveExam.objects.filter(start_time__gt=timezone.now()).order_by('start_time')[:5]
    recent_results = Result.objects.filter(user=request.user).order_by('-submission_time')[:5]
    notifications = Notification.objects.filter(user=request.user, is_read=False)[:5]
    recent_activities = UserActivity.objects.filter(user=request.user).order_by('-created_at')[:10]

    # Performance Metrics
    total_exams = Result.objects.filter(user=request.user).count()
    avg_score = Result.objects.filter(user=request.user).aggregate(Avg('score'))['score__avg'] or 0
    correct_answers = Result.objects.filter(user=request.user).aggregate(Sum('correct_answers'))['correct_answers__sum'] or 0
    wrong_answers = Result.objects.filter(user=request.user).aggregate(Sum('wrong_answers'))['wrong_answers__sum'] or 0

    # Service related data
    registrations = ExamRegistration.objects.filter(user=request.user).select_related('service')
    reviews = Review.objects.filter(user=request.user).select_related('service')
    promotions = get_active_promotions()

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
        'registrations': registrations,
        'reviews': reviews,
        'promotions': promotions,
    }
    return render(request, 'dashboard/dashboard.html', context)

@login_required
def performance_metrics(request):
    results = Result.objects.filter(user=request.user).order_by('submission_time')
    
    if not results.exists():
        messages.info(request, _('আপনার এখনও কোনও পরীক্ষার ফলাফল নেই।'))
        return redirect('dashboard:dashboard')

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

    context = {'graphic': graphic}
    return render(request, 'dashboard/performance_metrics.html', context)

@login_required
def customize_dashboard(request):
    if request.method == 'POST':
        layout = request.POST.get('layout')
        UserPreference.objects.update_or_create(
            user=request.user,
            defaults={'dashboard_layout': layout}
        )
        messages.success(request, _('ড্যাশবোর্ড লেআউট সফলভাবে আপডেট করা হয়েছে।'))
        return redirect('dashboard:user_dashboard')
    
    user_preference, created = UserPreference.objects.get_or_create(user=request.user)
    context = {'current_layout': user_preference.dashboard_layout}
    return render(request, 'dashboard/customize_dashboard.html', context)

@login_required
def submit_feedback(request):
    if request.method == 'POST':
        message = request.POST.get('message')
        if message:
            Feedback.objects.create(user=request.user, message=message)
            messages.success(request, _('আপনার প্রতিক্রিয়া সফলভাবে জমা দেওয়া হয়েছে। ধন্যবাদ!'))
        else:
            messages.error(request, _('দয়া করে একটি বার্তা লিখুন।'))
        return redirect('dashboard:dashboard')
    return render(request, 'dashboard/submit_feedback.html')

