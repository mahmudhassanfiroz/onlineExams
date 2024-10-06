from django.db import models
from django.utils import timezone
from accounts.models import CustomUser
from services.models import Package
from books.models import Book

class Discount(models.Model):
    code = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    is_percentage = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    valid_from = models.DateTimeField()
    valid_to = models.DateTimeField()
    max_uses = models.PositiveIntegerField(default=1)
    current_uses = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.code

class Payment(models.Model):
    PAYMENT_STATUS_CHOICES = [
        ('PENDING', 'অপেক্ষমান'),
        ('COMPLETED', 'সম্পন্ন'),
        ('FAILED', 'ব্যর্থ'),
        ('CANCELLED', 'বাতিল'),
    ]

    PAYMENT_TYPE_CHOICES = [
        ('PACKAGE', 'প্যাকেজ'),
        ('BOOK', 'বই'),
    ]

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_type = models.CharField(max_length=10, choices=PAYMENT_TYPE_CHOICES)
    status = models.CharField(max_length=10, choices=PAYMENT_STATUS_CHOICES, default='PENDING')
    transaction_id = models.CharField(max_length=255, unique=True, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # SSLCommerz specific fields
    tran_id = models.CharField(max_length=255, unique=True)
    val_id = models.CharField(max_length=255, null=True, blank=True)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    card_type = models.CharField(max_length=50, null=True, blank=True)
    card_no = models.CharField(max_length=50, null=True, blank=True)
    bank_tran_id = models.CharField(max_length=255, null=True, blank=True)
    card_issuer = models.CharField(max_length=255, null=True, blank=True)
    card_brand = models.CharField(max_length=50, null=True, blank=True)
    risk_level = models.IntegerField(null=True, blank=True)
    risk_title = models.CharField(max_length=50, null=True, blank=True)

    discount = models.ForeignKey(Discount, on_delete=models.SET_NULL, null=True, blank=True)
    discounted_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    book = models.ForeignKey(Book, on_delete=models.SET_NULL, null=True, blank=True)
    package = models.ForeignKey(Package, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.amount} - {self.get_payment_type_display()}"

    def apply_discount(self, discount):
        if discount.is_percentage:
            self.discounted_amount = self.amount - (self.amount * discount.amount / 100)
        else:
            self.discounted_amount = max(self.amount - discount.amount, 0)
        self.discount = discount
        self.save()

    def save(self, *args, **kwargs):
        if not self.tran_id:
            self.tran_id = f"TRAN-{timezone.now().timestamp()}"
        super().save(*args, **kwargs)



class Refund(models.Model):
    REFUND_STATUS_CHOICES = [
        ('PENDING', 'অপেক্ষমান'),
        ('APPROVED', 'অনুমোদিত'),
        ('REJECTED', 'প্রত্যাখ্যাত'),
        ('COMPLETED', 'সম্পন্ন'),
    ]

    payment = models.OneToOneField(Payment, on_delete=models.CASCADE)
    reason = models.TextField()
    status = models.CharField(max_length=10, choices=REFUND_STATUS_CHOICES, default='PENDING')
    requested_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    refunded_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return f"Refund for {self.payment}"

    def process_refund(self, status, refunded_amount=None):
        self.status = status
        self.processed_at = timezone.now()
        if status == 'COMPLETED':
            self.refunded_amount = refunded_amount or self.payment.amount
        self.save()

class PackagePurchase(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    package = models.ForeignKey(Package, on_delete=models.CASCADE)
    payment = models.OneToOneField(Payment, on_delete=models.CASCADE)
    purchase_date = models.DateTimeField(auto_now_add=True)
    expiry_date = models.DateTimeField()

    def __str__(self):
        return f"{self.user.username} - {self.package.name}"

    def save(self, *args, **kwargs):
        if not self.expiry_date:
            self.expiry_date = timezone.now() + self.package.duration
        super().save(*args, **kwargs)

class BookPurchase(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    payment = models.OneToOneField(Payment, on_delete=models.CASCADE)
    purchase_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'book')

    def __str__(self):
        return f"{self.user.username} - {self.book.title}"

    @classmethod
    def create_from_payment(cls, payment):
        return cls.objects.create(
            user=payment.user,
            book=payment.book,
            payment=payment
        )
