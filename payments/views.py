from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from online_job_exam.settings import SSLCZ_IS_SANDBOX, SSLCZ_STORE_ID, SSLCZ_STORE_PASSWORD
from .models import Payment, PackagePurchase, BookPurchase, Discount, Refund
from services.models import Package, UserPackage
from books.models import Book
from sslcommerz_lib import SSLCOMMERZ

@login_required
def initiate_payment(request, item_type, item_id):
    if item_type == 'PACKAGE':
        item = get_object_or_404(Package, id=item_id)
    elif item_type == 'BOOK':
        item = get_object_or_404(Book, id=item_id)
    else:
        messages.error(request, 'অবৈধ আইটেম টাইপ।')
        return redirect('home')

    payment = Payment.objects.create(
        user=request.user,
        amount=item.get_price(),
        payment_type=item_type,
        tran_id=f"{item_type}-{item.id}-{timezone.now().timestamp()}",
        book=item if item_type == 'BOOK' else None,
        package=item if item_type == 'PACKAGE' else None
    )


    if not payment:
        payment = Payment.objects.create(
            user=request.user,
            amount=item.price,
            payment_type=item_type,
            tran_id=f"{item_type}-{item.id}-{timezone.now().timestamp()}",
            book=item if item_type == 'BOOK' else None,
            package=item if item_type == 'PACKAGE' else None
        )

    mobile = request.user.mobile or "01700000000"  # ডিফল্ট নম্বর

    sslcz = SSLCOMMERZ({
        'store_id': SSLCZ_STORE_ID,
        'store_pass': SSLCZ_STORE_PASSWORD,
        'issandbox': SSLCZ_IS_SANDBOX
    })
    post_body = {
        'total_amount': float(payment.amount),
        'currency': "BDT",
        'tran_id': payment.tran_id,
        'success_url': request.build_absolute_uri(reverse('payments:payment_success')),
        'fail_url': request.build_absolute_uri(reverse('payments:payment_fail')),
        'cancel_url': request.build_absolute_uri(reverse('payments:payment_cancel')),
        'emi_option': 0,
        'cus_name': request.user.get_full_name(),
        'cus_email': request.user.email,
        'cus_phone': mobile,
        'product_category': item_type,
        'product_name': item.name if item_type == 'PACKAGE' else item.title,
        'shipping_method': 'NO',
        'product_profile': 'NON_PHYSICAL_GOODS',
        'cus_add1': 'Dhaka',
        'cus_city': 'Dhaka',
        'cus_country': 'Bangladesh',
    }

    try:
        response = sslcz.createSession(post_body)
        if 'status' in response and response['status'] == 'SUCCESS':
            if 'GatewayPageURL' in response and response['GatewayPageURL']:
                return redirect(response['GatewayPageURL'])
            else:
                messages.error(request, 'পেমেন্ট গেটওয়ে URL পাওয়া যায়নি।')
        else:
            error_message = response.get('failedreason', 'অজানা ত্রুটি ঘটেছে।')
            messages.error(request, f'পেমেন্ট সেশন তৈরি করতে ব্যর্থ: {error_message}')
    except Exception as e:
        messages.error(request, f'একটি ত্রুটি ঘটেছে: {str(e)}')

    if item_type == 'PACKAGE':
        return redirect('services:package_detail', slug=item.slug)
    else:
        return redirect('books:book_detail', book_id=item.id)


@login_required
def payment_success(request):
    payment = get_object_or_404(Payment, tran_id=request.POST['tran_id'])
    payment.status = 'COMPLETED'
    payment.val_id = request.POST['val_id']
    payment.card_type = request.POST['card_type']
    payment.card_no = request.POST['card_no']
    payment.bank_tran_id = request.POST['bank_tran_id']
    payment.save()

    if payment.payment_type == 'PACKAGE':
        package = Package.objects.get(id=payment.tran_id.split('-')[1])
        PackagePurchase.objects.create(user=payment.user, package=package, payment=payment)
        UserPackage.objects.create(
            user=payment.user,
            package=package,
            expiry_date=timezone.now() + package.duration
        )
    elif payment.payment_type == 'BOOK':
        book = Book.objects.get(id=payment.tran_id.split('-')[1])
        BookPurchase.objects.create(user=payment.user, book=book, payment=payment)

    messages.success(request, 'আপনার পেমেন্ট সফলভাবে সম্পন্ন হয়েছে।')
    return redirect('payments:payment_details', payment_id=payment.id)

@login_required
def payment_fail(request):
    payment = get_object_or_404(Payment, tran_id=request.POST['tran_id'])
    payment.status = 'FAILED'
    payment.save()
    messages.error(request, 'পেমেন্ট ব্যর্থ হয়েছে। অনুগ্রহ করে আবার চেষ্টা করুন।')
    return redirect('home')

@login_required
def payment_cancel(request):
    payment = get_object_or_404(Payment, tran_id=request.POST['tran_id'])
    payment.status = 'CANCELLED'
    payment.save()
    messages.info(request, 'আপনি পেমেন্ট বাতিল করেছেন।')
    return redirect('home')

@login_required
def payment_details(request, payment_id):
    payment = get_object_or_404(Payment, id=payment_id, user=request.user)
    context = {'payment': payment}
    return render(request, 'payments/payment_details.html', context)

@login_required
@require_POST
def apply_discount(request, payment_id):
    payment = get_object_or_404(Payment, id=payment_id, user=request.user)
    discount_code = request.POST.get('discount_code')
    
    try:
        discount = Discount.objects.get(code=discount_code, is_active=True)
        if discount.valid_from <= timezone.now() <= discount.valid_to and discount.current_uses < discount.max_uses:
            payment.apply_discount(discount)
            discount.current_uses += 1
            discount.save()
            messages.success(request, 'ডিসকাউন্ট সফলভাবে প্রয়োগ করা হয়েছে।')
        else:
            messages.error(request, 'এই ডিসকাউন্ট কোডটি বৈধ নয়।')
    except Discount.DoesNotExist:
        messages.error(request, 'অবৈধ ডিসকাউন্ট কোড।')
    
    return redirect('payment_details', payment_id=payment.id)

@login_required
def request_refund(request, payment_id):
    payment = get_object_or_404(Payment, id=payment_id, user=request.user)
    if request.method == 'POST':
        reason = request.POST.get('reason')
        Refund.objects.create(payment=payment, reason=reason)
        messages.success(request, 'আপনার রিফান্ড অনুরোধ জমা দেওয়া হয়েছে।')
        return redirect('payment_details', payment_id=payment.id)
    return render(request, 'payments/request_refund.html', {'payment': payment})

@login_required
def refund_list(request):
    refunds = Refund.objects.filter(payment__user=request.user)
    return render(request, 'payments/refund_list.html', {'refunds': refunds})

@login_required
def transaction_history(request):
    payments = Payment.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'payments/transaction_history.html', {'payments': payments})

