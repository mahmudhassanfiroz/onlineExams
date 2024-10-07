from django.db import models
from django.utils import timezone
from django.urls import reverse
from django_ckeditor_5.fields import CKEditor5Field
from django.core.exceptions import ValidationError
from django.utils.html import strip_tags
import json
from accounts.models import CustomUser

class MarqueeNotice(models.Model):
    message = CKEditor5Field()
    is_active = models.BooleanField(default=True)
    start_date = models.DateTimeField(default=timezone.now)
    end_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return strip_tags(self.message)[:50]

    def get_stripped_message(self):
        return strip_tags(self.message)

    class Meta:
        ordering = ['-start_date']

class CarouselSlide(models.Model):
    title = models.CharField(max_length=200)
    description = CKEditor5Field()
    image = models.ImageField(upload_to='carousel/')
    button_text = models.CharField(max_length=50, blank=True, null=True)
    button_url = models.CharField(max_length=200, blank=True, null=True)
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)

    def get_stripped_description(self):
        return strip_tags(self.description)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.title

class CTASection(models.Model):
    title = models.CharField(max_length=200)
    description = CKEditor5Field()
    button_text = models.CharField(max_length=50)
    button_url = models.CharField(max_length=200)
    is_active = models.BooleanField(default=True)

    def get_stripped_description(self):
        return strip_tags(self.description)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "CTA Section"
        verbose_name_plural = "CTA Sections"


class FooterContent(models.Model):
    contact_title = models.CharField(max_length=100, default="যোগাযোগ")
    email_label = models.CharField(max_length=100, default="ইমেইল")
    phone_label = models.CharField(max_length=100, default="ফোন")
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    quick_links_title = models.CharField(max_length=100, default="দ্রুত লিঙ্ক")
    social_media_title = models.CharField(max_length=100, default="সামাজিক মাধ্যম")
    facebook_url = models.URLField(blank=True)
    twitter_url = models.URLField(blank=True)
    linkedin_url = models.URLField(blank=True)
    instagram_url = models.URLField(blank=True)
    copyright_text = models.CharField(max_length=200)

    class Meta:
        verbose_name = "Footer Content"
        verbose_name_plural = "Footer Contents"

    def __str__(self):
        return "Footer Content"

    def clean(self):
        if FooterContent.objects.exists() and not self.pk:
            raise ValidationError("You can only have one Footer Content instance.")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

class QuickLink(models.Model):
    footer_content = models.ForeignKey(FooterContent, on_delete=models.CASCADE, related_name='quick_links')
    name = models.CharField(max_length=100)
    url = models.CharField(max_length=200)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']
        verbose_name = "Quick Link"
        verbose_name_plural = "Quick Links"

    def __str__(self):
        return self.name

class MenuItem(models.Model):
    name = models.CharField(max_length=100)
    url = models.CharField(max_length=200, blank=True)
    parent = models.ForeignKey('self', null=True, blank=True, related_name='children', on_delete=models.CASCADE)
    order = models.IntegerField(default=0)  # এই লাইনটি যোগ করুন

    class Meta:
        ordering = ['order']  # এটি এখন কাজ করবে

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        if self.url:
            return self.url
        elif self.children.exists():
            return '#'
        else:
            # এখানে আপনার প্রয়োজন অনুযায়ী URL জেনারেট করুন
            return reverse('services:category_detail', kwargs={'category_slug': self.name.lower()})

class SiteSettings(models.Model):
    site_title = models.CharField(max_length=100, default="জব পরীক্ষা প্ল্যাটফর্ম")
    site_logo = models.ImageField(upload_to='site_images/', null=True, blank=True)
    navbar_title = models.CharField(max_length=100, default="জব পরীক্ষা প্ল্যাটফর্ম")
    favicon = models.ImageField(upload_to='site_images/', null=True, blank=True)
    
    # নতুন ফিল্ডগুলি
    home_service_packages_title = models.CharField(max_length=100, default="আমাদের সার্ভিস প্যাকেজসমূহ")
    home_featured_packages_title = models.CharField(max_length=100, default="ফিচার্ড প্যাকেজসমূহ")
    home_testimonials_title = models.CharField(max_length=100, default="পরীক্ষার্থীদের মতামত")
    home_faq_title = models.CharField(max_length=100, default="সাধারণ জিজ্ঞাসা")
    home_dashboard_title = models.CharField(max_length=100, default="আপনার ড্যাশবোর্ড")
    home_next_exam_title = models.CharField(max_length=100, default="পরবর্তী পরীক্ষা")
    home_average_score_title = models.CharField(max_length=100, default="গড় স্কোর")
    home_latest_result_title = models.CharField(max_length=100, default="সর্বশেষ পরীক্ষার ফলাফল")

    class Meta:
        verbose_name = "Site Settings"
        verbose_name_plural = "Site Settings"

    def __str__(self):
        return "Site Settings"


class AboutPage(models.Model):
    title = models.CharField(max_length=200, default="আমাদের সম্পর্কে")
    heading = models.CharField(max_length=200, default="আমাদের সম্পর্কে")

    def __str__(self):
        return self.title

class AboutSection(models.Model):
    CONTENT_TYPES = (
        ('text', 'Text'),
        ('list', 'List'),
    )
    about_page = models.ForeignKey(AboutPage, on_delete=models.CASCADE, related_name='sections')
    title = models.CharField(max_length=200)
    content_type = models.CharField(max_length=10, choices=CONTENT_TYPES)
    content = CKEditor5Field()
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.title

class AboutButton(models.Model):
    section = models.OneToOneField(AboutSection, on_delete=models.CASCADE, related_name='button')
    text = models.CharField(max_length=50)
    url = models.CharField(max_length=200)

    def __str__(self):
        return self.text

class ContactPage(models.Model):
    title = models.CharField(max_length=200, default="যোগাযোগ করুন")
    heading = models.CharField(max_length=200, default="যোগাযোগ করুন")
    submit_button_text = models.CharField(max_length=50, default="বার্তা পাঠান")
    show_additional_info = models.BooleanField(default=True)
    additional_info_title = models.CharField(max_length=200, default="অন্যান্য যোগাযোগের মাধ্যম")

    def __str__(self):
        return self.title

class ContactAdditionalInfo(models.Model):
    contact_page = models.ForeignKey(ContactPage, on_delete=models.CASCADE, related_name='additional_info')
    icon = models.CharField(max_length=50)
    title = models.CharField(max_length=100)
    content = CKEditor5Field(max_length=200)
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.title

class Advertisement(models.Model):
    POSITION_CHOICES = [
        ('top', 'শীর্ষে'),
        ('bottom', 'নীচে'),
        ('sidebar', 'সাইডবারে')
    ]
    
    AD_TYPE_CHOICES = [
        ('custom', 'কাস্টম বিজ্ঞাপন'),
        ('google', 'Google Ads')
    ]

    title = models.CharField(max_length=200, verbose_name="শিরোনাম", null=True, blank=True)
    ad_type = models.CharField(max_length=10, choices=AD_TYPE_CHOICES, default='custom', verbose_name="বিজ্ঞাপনের ধরন")
    content = CKEditor5Field(verbose_name="বিষয়বস্তু", blank=True, null=True)
    image = models.ImageField(upload_to='advertisements/', blank=True, null=True, verbose_name="ছবি")
    url = models.URLField(blank=True, verbose_name="লিংক")
    google_ad_code = models.TextField(blank=True, verbose_name="Google Ads কোড")
    is_active = models.BooleanField(default=True, verbose_name="সক্রিয়")
    position = models.CharField(max_length=50, choices=POSITION_CHOICES, verbose_name="অবস্থান")

    class Meta:
        verbose_name = "বিজ্ঞাপন"
        verbose_name_plural = "বিজ্ঞাপনসমূহ"

    def __str__(self):
       return self.title or f"Advertisement {self.id}"

    def clean(self):
        if self.ad_type == 'custom':
            if not self.image and not self.url and not self.content:
                raise ValidationError("কাস্টম বিজ্ঞাপনের জন্য ইমেজ, URL অথবা কন্টেন্ট প্রয়োজন।")
        elif self.ad_type == 'google':
            if not self.google_ad_code:
                raise ValidationError("Google Ads এর জন্য Google Ads কোড প্রয়োজন।")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def get_ad_json(self):
        return json.dumps({
            'id': self.id,
            'type': self.ad_type,
            'content': self.get_ad_content(),
            'url': self.url,
            'title': self.title or f"বিজ্ঞাপন {self.id}",
            'image_url': self.image.url if self.image else None,
            'position': self.position,
            'is_active': self.is_active,
        })

    def get_ad_content(self):
        if self.ad_type == 'google':
            return self.google_ad_code
        else:
            if self.image:
                return f'<img src="{self.image.url}" alt="{self.title or "বিজ্ঞাপন"}">'
            return self.content or ""


class GeneralFeedback(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Feedback by {self.user.username} on {self.created_at}"

