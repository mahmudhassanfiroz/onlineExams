from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from .models import Package, UserPackage
from exams.models import Exam
from django.db.models import Prefetch

def package_detail(request, slug):
    package = get_object_or_404(Package, slug=slug)
    
    exams_by_category = {
        category: Exam.objects.filter(exam_category=category)
        for category in package.exam_categories.all()
    }

    context = {
        'package': package,
        'exams_by_category': exams_by_category,
    }
    return render(request, 'services/package_detail.html', context)

@login_required
def purchase_package(request, slug):
    package = get_object_or_404(Package, slug=slug)
    
    messages.info(request, f'{package.name} প্যাকেজের জন্য পেমেন্ট প্রক্রিয়া শুরু হচ্ছে।')
    return redirect('payments:initiate_payment', item_type='PACKAGE', item_id=package.id)

@login_required
def user_packages(request):
    user_packages = UserPackage.objects.filter(user=request.user, is_active=True)
    context = {
        'user_packages': user_packages,
    }
    return render(request, 'services/user_packages.html', context)

def search_packages(request):
    query = request.GET.get('q')
    packages = Package.objects.filter(name__icontains=query) if query else Package.objects.all()
    context = {
        'packages': packages,
        'query': query,
    }
    return render(request, 'services/search_packages.html', context)

