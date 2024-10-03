from django.shortcuts import render, redirect
from django.utils import timezone
from django.db.models import Q, Avg
from django.contrib import messages
from core.models import AboutPage, CTASection, CarouselSlide, MarqueeNotice, SiteSettings, ContactPage
from exams.models import ExamSchedule, ExamRegistration, ExamResult
from services.models import Package
from .forms import ContactForm
from .models import MarqueeNotice, CarouselSlide, CTASection, FooterContent

def home(request):
    context = {
        'featured_packages': Package.objects.filter(is_featured=True),
        'active_notices': MarqueeNotice.objects.filter(
            is_active=True,
            start_date__lte=timezone.now()
        ).filter(
            Q(end_date__isnull=True) | Q(end_date__gte=timezone.now())
        ),
        'active_slides': CarouselSlide.objects.filter(is_active=True).order_by('order'),
        'cta_section': CTASection.objects.filter(is_active=True).first(),
        'footer_content': FooterContent.objects.first(),  # FooterContent যোগ করা হয়েছে
    }

    next_exam = None
    next_exam_category_id = None

    if request.user.is_authenticated:
        next_exam = ExamRegistration.objects.filter(
            user=request.user,
            exam__exam_date__gt=timezone.now()
        ).select_related('exam__batch__category').order_by('exam__exam_date').first()

        context.update({
            'average_score': ExamResult.objects.filter(
                registration__user=request.user
            ).aggregate(Avg('score'))['score__avg'] or 0,
            'latest_result': ExamResult.objects.filter(
                registration__user=request.user
            ).order_by('-submitted_at').first(),
        })
    else:
        next_exam = ExamSchedule.objects.filter(
            exam_date__gt=timezone.now()
        ).select_related('batch__category').order_by('exam_date').first()

    if next_exam:
        if request.user.is_authenticated:
            next_exam_category = next_exam.exam.batch.category if next_exam.exam.batch else None
        else:
            next_exam_category = next_exam.batch.category if next_exam.batch else None
        
        next_exam_category_id = next_exam_category.id if next_exam_category else None

    context.update({
        'next_exam': next_exam,
        'next_exam_category_id': next_exam_category_id,
    })

    return render(request, 'core/home.html', context)


def about(request):
    about_page = AboutPage.objects.first()
    site_settings = SiteSettings.objects.first()
    
    context = {
        'about_page': about_page,
        'site_settings': site_settings,
    }
    return render(request, 'core/about.html', context)

def contact(request):
    contact_page = ContactPage.objects.first()
    site_settings = SiteSettings.objects.first()
    
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            # এখানে ফর্ম ডেটা প্রসেস করুন (যেমন ইমেইল পাঠানো)
            messages.success(request, 'আপনার বার্তা সফলভাবে পাঠানো হয়েছে।')
            return redirect('contact')
    else:
        form = ContactForm()
    
    context = {
        'contact_page': contact_page,
        'site_settings': site_settings,
        'form': form,
    }
    return render(request, 'core/contact.html', context)

