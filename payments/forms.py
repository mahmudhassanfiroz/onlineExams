
from django import forms
from .models import Payment, Refund

class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = []  # পেমেন্ট গেটওয়ে ইন্টিগ্রেশনের জন্য প্রয়োজনীয় ফিল্ড যোগ করুন

class RefundForm(forms.ModelForm):
    class Meta:
        model = Refund
        fields = ['reason']

