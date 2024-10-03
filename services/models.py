from datetime import timezone
import uuid
from django.db import models
from accounts.models import CustomUser
from django.forms import ValidationError
from django.utils.text import slugify
from django_ckeditor_5.fields import CKEditor5Field

class ServiceCategory(models.Model):
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='service_categories/', null=True, blank=True)
    description = CKEditor5Field()
    slug = models.SlugField(unique=True, blank=True)
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Service Category'
        verbose_name_plural = 'Service Categories'

    def __str__(self):
        return self.name

class Service(models.Model):
    category = models.ForeignKey(ServiceCategory, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    description = CKEditor5Field()
    features = models.TextField()
    is_free = models.BooleanField(default=False)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    image = models.ImageField(upload_to='services/', null=True, blank=True)
    slug = models.SlugField(unique=True, blank=True, max_length=200)
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
            if Service.objects.filter(slug=self.slug).exists():
                self.slug = f"{self.slug}-{uuid.uuid4().hex[:6]}"
        super().save(*args, **kwargs)
        
    def __str__(self):
        return self.name

class Package(models.Model):
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    description = CKEditor5Field()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    features = models.TextField()
    duration = models.DurationField()
    is_featured = models.BooleanField(default=False)
    
    def get_final_price(self, promotion_code=None):
        if promotion_code:
            try:
                promotion = Promotion.objects.get(
                    code=promotion_code,
                    service=self.service,
                    valid_from__lte=timezone.now(),
                    valid_to__gte=timezone.now()
                )
                discounted_price = self.price - (self.price * promotion.discount_percent / 100)
                return max(discounted_price, 0)  # নেগেটিভ মূল্য এড়াতে
            except Promotion.DoesNotExist:
                pass
        return self.price

    def __str__(self):
        return f"{self.service.name} - {self.name}"

class ServiceRegistration(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    package = models.ForeignKey(Package, on_delete=models.CASCADE)
    registration_date = models.DateTimeField(auto_now_add=True)
    payment_status = models.BooleanField(default=False)
    
    class Meta:
        unique_together = (('user', 'service', 'package'))

    def __str__(self):
        return f"{self.user.username} - {self.service.name}"


class Promotion(models.Model):
    title = models.CharField(max_length=200)
    description = CKEditor5Field()
    discount_percent = models.PositiveIntegerField()
    code = models.CharField(max_length=50, unique=True)
    valid_from = models.DateTimeField()
    valid_to = models.DateTimeField()
    service = models.ForeignKey('Service', on_delete=models.CASCADE, null=True, blank=True)
    image = models.ImageField(upload_to='promotion_images/', null=True, blank=True)

    def apply_discount(self, price):
        discounted_price = price - (price * self.discount_percent / 100)
        return max(discounted_price, 0)  # নেগেটিভ মূল্য এড়াতে

    def is_active(self):
        now = timezone.now()
        return self.valid_from <= now <= self.valid_to

    def __str__(self):
        return self.title


class Review(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    comment = CKEditor5Field()
    created_at = models.DateTimeField(auto_now_add=True) 
    
    def clean(self):
        if not 1 <= self.rating <= 5:
            raise ValidationError('Rating must be between 1 and 5.')

    def __str__(self):
        return f"{self.user.username} - {self.service.name} - {self.rating}"

class FAQ(models.Model):
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    question = CKEditor5Field()
    answer = CKEditor5Field()

    def __str__(self):
        return f"{self.service.name} - {self.question[:50]}"

