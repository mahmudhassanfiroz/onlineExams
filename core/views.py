from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.db.models import Q, Avg
from django.contrib import messages
from django.utils.html import strip_tags
from django.contrib.auth.decorators import login_required
from core.models import AboutPage, CTASection, CarouselSlide, MarqueeNotice, SiteSettings, ContactPage, FooterContent, MenuItem, Advertisement
from services.models import Package
from exams.models import UserExam
from liveExam.models import LiveExam, UserLiveExam
from results.models import Result, Feedback
from .forms import ContactForm
from .models import GeneralFeedback

def home(request):
    if request.method == 'POST' and request.user.is_authenticated:
        feedback_type = request.POST.get('feedback_type')
        comment = request.POST.get('comment')
        
        if feedback_type == 'general':
            GeneralFeedback.objects.create(user=request.user, comment=comment)
            messages.success(request, 'সাধারণ ফিডব্যাক সফলভাবে জমা দেওয়া হয়েছে।')
        elif feedback_type == 'result':
            result_id = request.POST.get('result_id')
            if result_id:
                result = get_object_or_404(Result, id=result_id)
                Feedback.objects.create(result=result, comment=comment)
                messages.success(request, 'রেজাল্ট ফিডব্যাক সফলভাবে জমা দেওয়া হয়েছে।')
        
        return redirect('home')

    context = {
        'featured_packages': Package.objects.filter(is_featured=True),
        'coaching_packages': Package.objects.filter(package_type='COACHING', is_featured=True),
        'student_packages': Package.objects.filter(package_type='STUDENT', is_featured=True),
        'active_notices': MarqueeNotice.objects.filter(
            is_active=True,
            start_date__lte=timezone.now()
        ).filter(
            Q(end_date__isnull=True) | Q(end_date__gte=timezone.now())
        ),
        'active_slides': CarouselSlide.objects.filter(is_active=True).order_by('order'),
        'cta_section': CTASection.objects.filter(is_active=True).first(),
        'footer_content': FooterContent.objects.first(),
        'menu_items': MenuItem.objects.filter(parent__isnull=True).order_by('order'),
        'site_settings': SiteSettings.objects.first(),
        'top_ads': Advertisement.objects.filter(is_active=True, position='top'),
        'bottom_ads': Advertisement.objects.filter(is_active=True, position='bottom'),
        'sidebar_ads': Advertisement.objects.filter(is_active=True, position='sidebar'),
    }

    # HTML ট্যাগ রিমুভ করা (মডেল মেথড ব্যবহার করে)
    context['active_notices'] = [notice.get_stripped_message() for notice in context['active_notices']]

    # সকল সাম্প্রতিক রেজাল্ট লোড করুন
    recent_results = Result.objects.all().order_by('-submission_time')[:5]
    context['recent_results'] = recent_results

    if request.user.is_authenticated:
        # Regular Exams
        user_exams = UserExam.objects.filter(user=request.user)
        context.update({
            'average_score_exams': user_exams.aggregate(Avg('score'))['score__avg'] or 0,
            'latest_exam_result': user_exams.order_by('-end_time').first(),
        })

        # Live Exams
        user_live_exams = UserLiveExam.objects.filter(user=request.user)
        context.update({
            'average_score_live_exams': user_live_exams.aggregate(Avg('score'))['score__avg'] or 0,
            'latest_live_exam_result': user_live_exams.order_by('-end_time').first(),
        })

        # Upcoming Live Exams
        upcoming_live_exams = LiveExam.objects.filter(
            exam_date__gte=timezone.now().date()
        ).order_by('exam_date', 'start_time')[:5]  # Get the next 5 upcoming exams
        context['upcoming_live_exams'] = upcoming_live_exams

    context['general_feedbacks'] = GeneralFeedback.objects.all().order_by('-created_at')[:5]

    return render(request, 'core/home.html', context)


def about(request):
    context = {
        'about_page': AboutPage.objects.first(),
        'site_settings': SiteSettings.objects.first(),
        'menu_items': MenuItem.objects.filter(parent__isnull=True).order_by('order'),
        'footer_content': FooterContent.objects.first(),
        'top_ads': Advertisement.objects.filter(is_active=True, position='top'),
        'bottom_ads': Advertisement.objects.filter(is_active=True, position='bottom'),
        'sidebar_ads': Advertisement.objects.filter(is_active=True, position='sidebar'),
    }
    return render(request, 'core/about.html', context)

def contact(request):
    contact_page = ContactPage.objects.first()
    site_settings = SiteSettings.objects.first()
    
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'আপনার বার্তা সফলভাবে পাঠানো হয়েছে।')
            return redirect('contact')
    else:
        form = ContactForm()
    
    context = {
        'contact_page': contact_page,
        'site_settings': site_settings,
        'form': form,
        'menu_items': MenuItem.objects.filter(parent__isnull=True).order_by('order'),
        'footer_content': FooterContent.objects.first(),
        'top_ads': Advertisement.objects.filter(is_active=True, position='top'),
        'bottom_ads': Advertisement.objects.filter(is_active=True, position='bottom'),
        'sidebar_ads': Advertisement.objects.filter(is_active=True, position='sidebar'),
    }
    return render(request, 'core/contact.html', context)