from django.urls import path
from . import views

app_name = 'payments'


urlpatterns = [
    path('initiate/<str:item_type>/<int:item_id>/', views.initiate_payment, name='initiate_payment'),
    path('success/', views.payment_success, name='payment_success'),
    path('fail/', views.payment_fail, name='payment_fail'),
    path('cancel/', views.payment_cancel, name='payment_cancel'),
    path('details/<int:payment_id>/', views.payment_details, name='payment_details'),
    path('apply-discount/<int:payment_id>/', views.apply_discount, name='apply_discount'),
    path('request-refund/<int:payment_id>/', views.request_refund, name='request_refund'),
    path('refunds/', views.refund_list, name='refund_list'),
    path('transaction-history/', views.transaction_history, name='transaction_history'),
]
