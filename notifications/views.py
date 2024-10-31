from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import Notification, NotificationPreference

@login_required
def notification_list(request):
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at').select_related('user')
    return render(request, 'notifications/notification_list.html', {'notifications': notifications})

@login_required
def notification_detail(request, notification_id):
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    notification.mark_as_read()
    return render(request, 'notifications/notification_detail.html', {'notification': notification})

@login_required
@require_POST
def mark_notification_as_read(request, notification_id):
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    notification.mark_as_read()
    return JsonResponse({'status': 'success'})

@login_required
def update_notification_preferences(request):
    preference, created = NotificationPreference.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        preference.live_exam = request.POST.get('live_exam') == 'on'
        preference.exam_result = request.POST.get('exam_result') == 'on'
        preference.blog_post = request.POST.get('blog_post') == 'on'
        preference.book_purchase = request.POST.get('book_purchase') == 'on'
        preference.general_info = request.POST.get('general_info') == 'on'
        preference.upcoming_exam = request.POST.get('upcoming_exam') == 'on'
        preference.login = request.POST.get('login') == 'on'
        preference.package_purchase = request.POST.get('package_purchase') == 'on'
        preference.save()
        return redirect('notifications:update_notification_preferences')
    
    return render(request, 'notifications/preferences.html', {'preference': preference})

