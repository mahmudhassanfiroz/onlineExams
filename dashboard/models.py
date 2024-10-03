from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from accounts.models import CustomUser
from liveExam.models import LiveExam, Batch 
from django_ckeditor_5.fields import CKEditor5Field

class UserProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='dashboard_profile')
    bio = CKEditor5Field(_("জীবনী"), max_length=500, blank=True)
    birth_date = models.DateField(_("জন্ম তারিখ"), null=True, blank=True)
    location = models.CharField(_("অবস্থান"), max_length=30, blank=True)
    website = models.URLField(_("ওয়েবসাইট"), max_length=100, blank=True)

    class Meta:
        verbose_name = _("ব্যবহারকারী প্রোফাইল")
        verbose_name_plural = _("ব্যবহারকারী প্রোফাইলসমূহ")

    def __str__(self):
        return f"{self.user.name}'s প্রোফাইল"


class UserActivity(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='activities')
    activity_type = models.CharField(_("কার্যক্রমের ধরন"), max_length=100)
    description = CKEditor5Field(_("বিবরণ"))
    created_at = models.DateTimeField(_("তৈরির সময়"), auto_now_add=True)

    class Meta:
        verbose_name = _("ব্যবহারকারী কার্যক্রম")
        verbose_name_plural = _("ব্যবহারকারী কার্যক্রমসমূহ")
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.name} - {self.activity_type}"

class UserPreference(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='preferences')
    dashboard_layout = models.JSONField(_("ড্যাশবোর্ড লেআউট"), default=dict)

    class Meta:
        verbose_name = _("ব্যবহারকারী পছন্দ")
        verbose_name_plural = _("ব্যবহারকারী পছন্দসমূহ")

    def __str__(self):
        return f"{self.user.name}'s পছন্দসমূহ"

class Badge(models.Model):
    name = models.CharField(_("নাম"), max_length=100)
    description = CKEditor5Field(_("বিবরণ"))
    icon = models.ImageField(_("আইকন"), upload_to='badges/')

    class Meta:
        verbose_name = _("ব্যাজ")
        verbose_name_plural = _("ব্যাজসমূহ")

    def __str__(self):
        return self.name

class UserBadge(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='badges')
    badge = models.ForeignKey(Badge, on_delete=models.CASCADE)
    earned_at = models.DateTimeField(_("অর্জনের সময়"), auto_now_add=True)

    class Meta:
        verbose_name = _("ব্যবহারকারী ব্যাজ")
        verbose_name_plural = _("ব্যবহারকারী ব্যাজসমূহ")
        unique_together = ('user', 'badge')

    def __str__(self):
        return f"{self.user.name} - {self.badge.name}"

class Feedback(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='feedbacks')
    message = CKEditor5Field(_("বার্তা"))
    created_at = models.DateTimeField(_("তৈরির সময়"), auto_now_add=True)

    class Meta:
        verbose_name = _("প্রতিক্রিয়া")
        verbose_name_plural = _("প্রতিক্রিয়াসমূহ")
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.name} - {self.message[:50]}..."
    
    