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
from dashboard.forms import DashboardCustomizationForm
from .models import UserActivity, UserPreference, UserBadge, Feedback, UserProfile
from liveExam.models import LiveExam, UserLiveExam
from results.models import Result
from exams.models import UserExam
from django.contrib.contenttypes.models import ContentType

def get_user_exam_content_types(user):
    """Retrieve content types for user exams and live exams."""
    user_live_exam_content_type = ContentType.objects.get_for_model(UserLiveExam)
    user_exam_content_type = ContentType.objects.get_for_model(UserExam)
    return user_live_exam_content_type, user_exam_content_type

@login_required
def user_dashboard(request):
    user_profile, _ = UserProfile.objects.get_or_create(user=request.user)
    user_preference, _ = UserPreference.objects.get_or_create(user=request.user)
    
    upcoming_exams = LiveExam.objects.filter(start_time__gt=timezone.now()).order_by('start_time')[:5]
    
    user_live_exam_content_type, user_exam_content_type = get_user_exam_content_types(request.user)
    
    recent_results = Result.objects.filter(
        Q(content_type=user_live_exam_content_type, object_id__in=UserLiveExam.objects.filter(user=request.user).values_list('id', flat=True)) |
        Q(content_type=user_exam_content_type, object_id__in=UserExam.objects.filter(user=request.user).values_list('id', flat=True))
    ).select_related('content_type').order_by('-submission_time')[:5]
    
    notifications = Notification.objects.filter(user=request.user, is_read=False)[:5]
    recent_activities = UserActivity.objects.filter(user=request.user).order_by('-created_at')[:10]

    # Performance Metrics
    user_results = Result.objects.filter(
        Q(content_type=user_live_exam_content_type, object_id__in=UserLiveExam.objects.filter(user=request.user).values_list('id', flat=True)) |
        Q(content_type=user_exam_content_type, object_id__in=UserExam.objects.filter(user=request.user).values_list('id', flat=True))
    )
    total_exams = user_results.count()
    avg_score = round(user_results.aggregate(Avg('score'))['score__avg'] or 0, 2)
    correct_answers = user_results.aggregate(Sum('correct_answers'))['correct_answers__sum'] or 0
    wrong_answers = user_results.aggregate(Sum('wrong_answers'))['wrong_answers__sum'] or 0

    # Organize performance metrics
    performance_metrics = [
        {'label': 'মোট পরীক্ষা', 'value': total_exams},
        {'label': 'গড় স্কোর', 'value': f"{avg_score:.2f}%"},
        {'label': 'সঠিক উত্তর', 'value': correct_answers},
        {'label': 'ভুল উত্তর', 'value': wrong_answers},
    ]

    default_widget_order = [
        'user_overview',
        'performance_metrics',
        'recent_results',
        'notifications',
        'recent_activities',
        'quick_links'
    ]

    if not user_preference.widget_order:
        user_preference.widget_order = default_widget_order
        user_preference.save()
    
    widget_order = user_preference.widget_order if isinstance(user_preference.widget_order, list) else user_preference.widget_order.split(',')

    widget_data = {
        'user_overview': {'user_profile': user_profile},
        'performance_metrics': {'metrics': performance_metrics},
        'recent_results': {'recent_results': recent_results},
        'notifications': {'notifications': notifications},
        'recent_activities': {'recent_activities': recent_activities},
        'quick_links': {},
        'upcoming_exams': {'upcoming_exams': upcoming_exams}
    }

    selected_widgets = {widget: widget_data[widget] for widget in widget_order if widget in widget_data}
    
    quick_links = [
        ('exams:exam_list', 'পরীক্ষা তালিকা'),
        ('results:overview', 'ফলাফল সারসংক্ষেপ'),
        ('accounts:account_settings', 'একাউন্ট সেটিংস'),
        ('dashboard:customize_dashboard', 'ড্যাশবোর্ড কাস্টমাইজ করুন'),
        ('dashboard:submit_feedback', 'প্রতিক্রিয়া জানান')
    ]
    
    context = {
        'user_profile': user_profile,
        'user_preference': user_preference,
        'widget_order': widget_order,
        'widgets': selected_widgets,
        'quick_links': quick_links,
    }
    return render(request, 'dashboard/dashboard.html', context)

@login_required
def performance_analysis(request):
    user_live_exam_content_type, user_exam_content_type = get_user_exam_content_types(request.user)

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

    graphic = base64.b64encode(image_png).decode('utf-8')

    context = {
        'graphic': graphic,
        'results': results,
    }
    return render(request, 'dashboard/performance_metrics.html', context)

@login_required
def customize_dashboard(request):
    user_preference, created = UserPreference.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        layout = request.POST.get('layout')
        color_scheme = request.POST.get('color_scheme')
        widget_order = request.POST.get('widget_order')

        user_preference.dashboard_layout = layout
        user_preference.color_scheme = color_scheme
        user_preference.widget_order = widget_order.split(',')
        user_preference.save()

        messages.success(request, 'ড্যাশবোর্ড কাস্টমাইজেশন সফলভাবে সংরক্ষিত হয়েছে।')
        return redirect('dashboard:user_dashboard')

    # Defining layout, color, and widget options
    layout_options = ["default", "compact", "expanded"]
    color_options = ["light", "dark", "blue"]
    widget_options = ["recent_activity", "upcoming_exams", "performance_metrics", "notifications"]
    
    context = {
        'current_layout': user_preference.dashboard_layout,
        'current_color_scheme': user_preference.color_scheme,
        'current_widget_order': user_preference.widget_order,
        'layout_options': layout_options,
        'color_options': color_options,
        'widget_options': widget_options,
    }
    
    return render(request, 'dashboard/customize_dashboard.html', context)

@login_required
def submit_feedback(request):
    if request.method == 'POST':
        message = request.POST.get('message')
        if message:
            Feedback.objects.create(user=request.user, message=message)
            messages.success(request, _('আপনার প্রতিক্রিয়া সফলভাবে জমা দেওয়া হয়েছে। ধন্যবাদ!'))
            return redirect('dashboard:user_dashboard')
        else:
            messages.error(request, _('দয়া করে একটি বার্তা লিখুন।'))
    return render(request, 'dashboard/submit_feedback.html')

@login_required
def change_profile_picture(request):
    if request.method == 'POST' and request.FILES.get('profile_picture'):
        user_profile, created = UserProfile.objects.get_or_create(user=request.user)
        user_profile.profile_image = request.FILES['profile_picture']
        user_profile.save()
        messages.success(request, 'প্রোফাইল ছবি সফলভাবে পরিবর্তন করা হয়েছে।')
    else:
        messages.error(request, 'প্রোফাইল ছবি আপলোড করতে ব্যর্থ হয়েছে। অনুগ্রহ করে আবার চেষ্টা করুন।')
    return redirect('dashboard:user_dashboard')
