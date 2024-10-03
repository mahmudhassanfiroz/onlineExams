from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.http import HttpResponse
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from sslcommerz_lib import SSLCOMMERZ
from decimal import Decimal
import requests

from notifications.utils import send_notification
from .models import Payment, PurchaseHistory, DiscountCode
from .forms import RefundForm
from books.models import Book
from exams.models import ExamRegistration

@login_required
def process_payment(request, item_type, item_id):
    if item_type == 'book':
        item = get_object_or_404(Book, pk=item_id)
        amount = item.price
        product_name = f"Book: {item.title}"
    elif item_type == 'exam':
        item = get_object_or_404(ExamRegistration, pk=item_id, user=request.user)
        if item.price:
            amount = item.price
        elif item.package and item.package.price:
            amount = item.package.price
        elif item.service and item.service.price:
            amount = item.service.price
        else:
            messages.error(request, 'মূল্য নির্ধারণে সমস্যা হয়েছে। দয়া করে অ্যাডমিনের সাথে যোগাযোগ করুন।')
            return redirect('home')  # অথবা অন্য কোন উপযুক্ত পৃষ্ঠায় রিডাইরেক্ট করুন
        product_name = f"Exam: {item.exam.exam.title}" if item.exam and item.exam.exam else "Exam"
    else:
        messages.error(request, 'অবৈধ আইটেম টাইপ।')
        return redirect('home')

    # চেক করুন যে পেমেন্ট ইতিমধ্যে করা হয়েছে কিনা
    existing_payment = Payment.objects.filter(
        user=request.user,
        book=item if item_type == 'book' else None,
        exam_registration=item if item_type == 'exam' else None,
        status='completed'
    ).first()

    if existing_payment:
        messages.info(request, 'আপনি ইতিমধ্যে এই আইটেমের জন্য পেমেন্ট করেছেন।')
        return redirect('home')  # অথবা অন্য কোন উপযুক্ত পৃষ্ঠায় রিডাইরেক্ট করুন

    payment = Payment.objects.create(
        user=request.user,
        book=item if item_type == 'book' else None,
        exam_registration=item if item_type == 'exam' else None,
        amount=amount,
        status='pending'
    )

    sslcz = SSLCOMMERZ({
        'store_id': settings.SSLCZ_STORE_ID,
        'store_pass': settings.SSLCZ_STORE_PASSWORD,
        'issandbox': settings.SSLCZ_IS_SANDBOX
    })

    post_body = {
        'total_amount': float(payment.amount),
        'currency': "BDT",
        'tran_id': str(payment.id),
        'success_url': request.build_absolute_uri(reverse('payments:payment_success')),
        'fail_url': request.build_absolute_uri(reverse('payments:payment_failed')),
        'cancel_url': request.build_absolute_uri(reverse('payments:payment_canceled')),
        'ipn_url': request.build_absolute_uri(reverse('payments:payment_ipn')),
        'emi_option': 0,
        'cus_name': request.user.get_full_name(),
        'cus_email': request.user.email,
        'cus_phone': request.user.phone,
        'cus_add1': request.user.address,
        'cus_city': request.user.city,
        'cus_country': "Bangladesh",
        'shipping_method': "NO",
        'multi_card_name': "",
        'num_of_item': 1,
        'product_name': product_name,
        'product_category': "Payment",
        'product_profile': "general",
    }

    response = sslcz.createSession(post_body)
    
    if response['status'] == 'SUCCESS':
        return redirect(response['GatewayPageURL'])
    else:
        messages.error(request, 'পেমেন্ট শুরু করতে সমস্যা হয়েছে। দয়া করে আবার চেষ্টা করুন।')
        return redirect('home')

@csrf_exempt
def payment_success(request):
    payment_id = request.POST.get('tran_id')
    payment = get_object_or_404(Payment, id=payment_id)
    payment.status = 'completed'
    payment.transaction_id = request.POST.get('bank_tran_id')
    payment.gateway_response = request.POST
    payment.save()

    if payment.book:
        PurchaseHistory.objects.create(user=payment.user, book=payment.book, payment=payment)
        send_notification(
            payment.user,
            'book_purchase',
            f'বই ক্রয় সফল: {payment.book.title}',
            f'আপনি সফলভাবে "{payment.book.title}" বইটি কিনেছেন।',
            payment.book
        )
        messages.success(request, 'আপনার বই কেনা সফল হয়েছে!')
        return redirect('books:download_book', book_id=payment.book.id)
    elif payment.exam_registration:
        payment.exam_registration.is_paid = True
        payment.exam_registration.save()
        send_notification(
            payment.user,
            'exam_registration',
            f'পরীক্ষা রেজিস্ট্রেশন সফল: {payment.exam_registration.exam.name}',
            f'আপনি সফলভাবে "{payment.exam_registration.exam.name}" পরীক্ষার জন্য রেজিস্ট্রেশন করেছেন।',
            payment.exam_registration
        )
        messages.success(request, 'আপনার পরীক্ষা রেজিস্ট্রেশন সফল হয়েছে!')
        return redirect('exams:exam_confirmation', registration_id=payment.exam_registration.id)
    
    messages.success(request, 'আপনার পেমেন্ট সফল হয়েছে!')
    return redirect('payments:transaction_history')

@csrf_exempt
def payment_failed(request):
    messages.error(request, 'পেমেন্ট ব্যর্থ হয়েছে। দয়া করে আবার চেষ্টা করুন।')
    return redirect('home')

@csrf_exempt
def payment_canceled(request):
    messages.warning(request, 'পেমেন্ট বাতিল করা হয়েছে।')
    return redirect('home')

@csrf_exempt
@require_POST
def payment_ipn(request):
    payment_data = request.POST
    tran_id = payment_data.get('tran_id', '')
    status = payment_data.get('status', '')

    try:
        payment = Payment.objects.get(id=tran_id)
    except Payment.DoesNotExist:
        return HttpResponse("Invalid Transaction", status=400)

    validation_url = f"{settings.SSLCZ_VALIDATION_URL}?val_id={payment_data.get('val_id', '')}&store_id={settings.SSLCZ_STORE_ID}&store_passwd={settings.SSLCZ_STORE_PASSWORD}&format=json"
    
    response = requests.get(validation_url)
    
    if response.status_code == 200:
        validation_data = response.json()
        
        if validation_data['status'] == 'VALID' or validation_data['status'] == 'VALIDATED':
            if status == 'VALID':
                payment.status = 'completed'
                payment.transaction_id = payment_data.get('bank_tran_id', '')
                payment.gateway_response = payment_data
                payment.save()

                if payment.book:
                    PurchaseHistory.objects.create(user=payment.user, book=payment.book, payment=payment)
                elif payment.exam_registration:
                    payment.exam_registration.is_paid = True
                    payment.exam_registration.save()

                send_payment_confirmation_email(payment)

            elif status == 'FAILED':
                payment.status = 'failed'
                payment.save()
            elif status == 'CANCELLED':
                payment.status = 'cancelled'
                payment.save()

            return HttpResponse("IPN Processed", status=200)
        
    return HttpResponse("IPN Processing Failed", status=400)

def send_payment_confirmation_email(payment):
    subject = 'পেমেন্ট নিশ্চিতকরণ'
    if payment.book:
        message = f'প্রিয় {payment.user.username},\n\nআপনার "{payment.book.title}" বইয়ের জন্য {payment.amount} টাকার পেমেন্ট সফলভাবে সম্পন্ন হয়েছে। আপনার লেনদেন আইডি: {payment.transaction_id}\n\nধন্যবাদ।'
    elif payment.exam_registration:
        message = f'প্রিয় {payment.user.username},\n\nআপনার "{payment.exam_registration.exam.name}" পরীক্ষার রেজিস্ট্রেশনের জন্য {payment.amount} টাকার পেমেন্ট সফলভাবে সম্পন্ন হয়েছে। আপনার লেনদেন আইডি: {payment.transaction_id}\n\nধন্যবাদ।'
    
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [payment.user.email])

@login_required
def transaction_history(request):
    transactions = Payment.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'payments/transaction_history.html', {'transactions': transactions})

@login_required
def refund_request(request, payment_id):
    payment = get_object_or_404(Payment, id=payment_id, user=request.user)
    
    if request.method == 'POST':
        form = RefundForm(request.POST)
        if form.is_valid():
            refund = form.save(commit=False)
            refund.payment = payment
            refund.save()
            messages.success(request, 'আপনার ফেরতের আবেদন জমা দেওয়া হয়েছে।')
            return redirect('payments:transaction_history')
    else:
        form = RefundForm()

    return render(request, 'payments/refund_request.html', {'form': form, 'payment': payment})

@login_required
def apply_discount(request):
    if request.method == 'POST':
        code = request.POST.get('discount_code')
        item_type = request.POST.get('item_type')
        item_id = request.POST.get('item_id')
        try:
            discount = DiscountCode.objects.get(code=code, is_active=True, valid_from__lte=timezone.now(), valid_to__gte=timezone.now())
            request.session['discount_code'] = discount.code
            messages.success(request, f'{discount.discount_percent}% ডিসকাউন্ট প্রযোজ্য হয়েছে।')
        except DiscountCode.DoesNotExist:
            messages.error(request, 'অবৈধ বা মেয়াদোত্তীর্ণ ডিসকাউন্ট কোড।')
    return redirect('payments:process_payment', item_type=item_type, item_id=item_id)