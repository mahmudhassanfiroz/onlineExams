from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    # পেমেন্ট প্রক্রিয়া
    path('process/<str:item_type>/<int:item_id>/', views.process_payment, name='process_payment'),
    path('success/', views.payment_success, name='payment_success'),
    path('failed/', views.payment_failed, name='payment_failed'),
    path('canceled/', views.payment_canceled, name='payment_canceled'),
    path('ipn/', views.payment_ipn, name='payment_ipn'),

    # পেমেন্ট ইতিহাস এবং রিফান্ড
    path('history/', views.transaction_history, name='transaction_history'),
    path('refund/<int:payment_id>/', views.refund_request, name='refund_request'),

    # ডিসকাউন্ট
    path('apply-discount/', views.apply_discount, name='apply_discount'),
]
