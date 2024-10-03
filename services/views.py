from django.utils import timezone 
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required

from exams.models import ExamCategory, Batch, ExamRegistration, ExamSchedule
from .models import ServiceCategory, Service, Package, ServiceRegistration, Promotion, Review, FAQ
from .forms import ServiceRegistrationForm, ReviewForm
from payments.models import Payment

def service_category_list(request):
    categories = ServiceCategory.objects.all()
    return render(request, 'services/category_list.html', {'categories': categories})

def service_category_detail(request, category_slug):
    category = get_object_or_404(ServiceCategory, slug=category_slug)
    services = Service.objects.filter(category=category)
    exam_categories = ExamCategory.objects.filter(service__category=category)
    
    # এখানে আমরা সরাসরি Batch কুয়েরি করছি
    batches = Batch.objects.filter(category__service__category=category).order_by('-start_date')
    
    context = {
        'category': category,
        'services': services,
        'exam_categories': exam_categories,
        'batches': batches,
    }
    return render(request, 'services/category_detail.html', context)

def service_detail(request, category_slug, service_slug):
    category = get_object_or_404(ServiceCategory, slug=category_slug)
    service = get_object_or_404(Service, category=category, slug=service_slug)    
    packages = Package.objects.filter(service=service)
    reviews = Review.objects.filter(service=service)
    faqs = FAQ.objects.filter(service=service)
    exams = ExamCategory.objects.filter(service=service)
    
    context = {
        'service': service,
        'packages': packages,
        'reviews': reviews,
        'faqs': faqs,
        'exams': exams,
    }
    return render(request, 'services/service_detail.html', context)



def save_service_registration(form, user, service):
    registration = form.save(commit=False)
    registration.user = user
    registration.service = service
    registration.save()
    return registration

@login_required
def service_registration(request, slug):
    user = request.user
    service = get_object_or_404(Service, slug=slug)

    # Get the package from the query parameter
    package_id = request.GET.get('package')
    package = None
    if package_id:
        package = get_object_or_404(Package, id=package_id, service=service)

    # প্রথমে সার্ভিসের জন্য একটি ExamSchedule খুঁজে নিন
    exam_schedule = ExamSchedule.objects.filter(batch__category__service=service).first()

    if not exam_schedule:
        messages.error(request, 'এই সেবার জন্য কোনো পরীক্ষা শিডিউল করা হয়নি।')
        return redirect('services:service_detail', category_slug=service.category.slug, service_slug=slug)

    # চেক করুন যে রেজিস্ট্রেশন ইতিমধ্যে বিদ্যমান কিনা
    existing_registration = ExamRegistration.objects.filter(
        user=user,
        exam=exam_schedule
    ).first()

    if existing_registration:
        if existing_registration.payment_status:
            messages.info(request, 'আপনি ইতিমধ্যে এই পরীক্ষার জন্য রেজিস্টার করেছেন এবং পেমেন্ট সম্পন্ন করেছেন।')
            # পরীক্ষা শুরু করার পৃষ্ঠায় রিডাইরেক্ট করুন
            return redirect('exams:start_exam', exam_id=exam_schedule.id)
        else:
            # পেমেন্ট সম্পন্ন হয়নি, পেমেন্ট পৃষ্ঠায় রিডাইরেক্ট করুন
            messages.info(request, 'আপনার রেজিস্ট্রেশন সম্পন্ন হয়েছে। এখন পেমেন্ট করুন।')
            return redirect('payments:process_payment', item_type='exam', item_id=existing_registration.id)

    if request.method == 'POST':
        form = ServiceRegistrationForm(request.POST)
        if form.is_valid():
            if not package:
                package = form.cleaned_data['package']

            # ExamRegistration অবজেক্ট তৈরি করুন
            exam_registration = ExamRegistration.objects.create(
                user=user,
                exam=exam_schedule,
                payment_status=False,
                price=package.price if package else service.price
            )

            # ServiceRegistration অবজেক্ট তৈরি করুন
            ServiceRegistration.objects.create(
                user=user,
                service=service,
                package=package
            )

            messages.success(request, 'আপনার রেজিস্ট্রেশন সফল হয়েছে। এখন পেমেন্ট করুন।')
            return redirect('payments:process_payment', item_type='exam', item_id=exam_registration.id)
    else:
        initial_data = {'service': service}
        if package:
            initial_data['package'] = package
        form = ServiceRegistrationForm(initial=initial_data)

    context = {
        'form': form,
        'service': service,
        'package': package
    }
    return render(request, 'services/service_registration.html', context)


@login_required
def add_review(request, category_slug, service_slug):
    category = get_object_or_404(ServiceCategory, slug=category_slug)
    service = get_object_or_404(Service, category=category, slug=service_slug)
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.service = service
            review.save()
            messages.success(request, 'আপনার রিভিউ সফলভাবে যোগ করা হয়েছে।')
            return redirect('services:service_detail', category_slug=category_slug, service_slug=service_slug)
    else:
        form = ReviewForm()
    return render(request, 'services/add_review.html', {'form': form, 'service': service})



def save_review(form, user, service):
    review = form.save(commit=False)
    review.user = user
    review.service = service
    review.save()
    return review


def get_active_promotions():
    return Promotion.objects.filter(valid_to__gte=timezone.now())

def promotions(request):
    active_promotions = get_active_promotions()
    return render(request, 'services/promotions.html', {'promotions': active_promotions})

def service_faq(request, slug):
    service = get_object_or_404(Service, slug=slug)
    faqs = FAQ.objects.filter(service=service)
    
    context = {
        'service': service,
        'faqs': faqs,
    }
    
    return render(request, 'services/service_faq.html', context)