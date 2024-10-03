from django.db import models
from accounts.models import CustomUser
from liveExam.models import LiveExam
from exams.models import ExamRegistration
from django.utils import timezone

from books.models import Book
from django_ckeditor_5.fields import CKEditor5Field
class PaymentPlan(models.Model):
    name = models.CharField(max_length=100)
    description = CKEditor5Field()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    duration = models.PositiveIntegerField(help_text="Duration in days")

    def __str__(self):
        return self.name

class Payment(models.Model):
    ORDER_STATUS_CHOICES = (
        ('pending', 'অপেক্ষমান'),
        ('processing', 'প্রক্রিয়াধীন'),
        ('completed', 'সম্পন্ন'),
        ('failed', 'ব্যর্থ'),
        ('cancelled', 'বাতিল'),
        ('refunded', 'ফেরত দেওয়া হয়েছে')
    )

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.SET_NULL, null=True, blank=True)  # এখানে পরিবর্তন করুন
    exam_registration = models.ForeignKey(ExamRegistration, on_delete=models.CASCADE, null=True, blank=True)
    order_number = models.CharField(max_length=50, unique=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    final_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=ORDER_STATUS_CHOICES, default='pending')
    transaction_id = models.CharField(max_length=100, unique=True)
    gateway_response = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"অর্ডার {self.order_number} - {self.user.username} - {self.exam_registration.exam.name if self.exam_registration else 'N/A'} - {self.final_amount}"

    def save(self, *args, **kwargs):
        if not self.order_number:
            self.order_number = f"ORD-{timezone.now().strftime('%Y%m%d%H%M%S')}-{self.user.id}"
        if not self.transaction_id:
            self.transaction_id = f"TXN-{timezone.now().timestamp()}"
        self.final_amount = self.amount - self.discount_amount
        super().save(*args, **kwargs)


class Refund(models.Model):
    REFUND_STATUS_CHOICES = (
        ('pending', 'অপেক্ষমান'),
        ('approved', 'অনুমোদিত'),
        ('rejected', 'প্রত্যাখ্যাত'),
        ('completed', 'সম্পন্ন'),
    )

    payment = models.ForeignKey(Payment, on_delete=models.CASCADE)
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=REFUND_STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.payment.user.username} - {self.payment.amount} - {self.status}"

class DiscountCode(models.Model):
    code = models.CharField(max_length=50, unique=True)
    discount_percent = models.PositiveIntegerField()
    valid_from = models.DateTimeField()
    valid_to = models.DateTimeField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.code

class PurchaseHistory(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.SET_NULL, null=True, blank=True)  # এখানে পরিবর্তন করুন
    payment = models.ForeignKey(Payment, on_delete=models.SET_NULL, null=True)
    exam_registration = models.ForeignKey(ExamRegistration, on_delete=models.CASCADE)
    purchase_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.exam_registration.exam.name}"


