from django.db import models
from django.utils.text import slugify
from django_ckeditor_5.fields import CKEditor5Field
from accounts.models import CustomUser

class ExamCategory(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True)
    description = CKEditor5Field()
    image = models.ImageField(upload_to='exam_categories/', null=True, blank=True)
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class Package(models.Model):
    PACKAGE_TYPES = (
        ('COACHING', 'কোচিং'),
        ('STUDENT', 'ছাত্র-ছাত্রী'),
    )
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True)
    description = CKEditor5Field()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    duration = models.DurationField()
    package_type = models.CharField(max_length=10, choices=PACKAGE_TYPES)
    exam_categories = models.ManyToManyField(ExamCategory)
    is_featured = models.BooleanField(default=False)
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
    
    def get_price(self):
        return self.price


class UserPackage(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    package = models.ForeignKey(Package, on_delete=models.CASCADE)
    purchase_date = models.DateTimeField(auto_now_add=True)
    expiry_date = models.DateTimeField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.user.username} - {self.package.name}"
