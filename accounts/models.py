# accounts/models.py

from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.contrib.auth.base_user import BaseUserManager
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.core.validators import RegexValidator
from django.conf import settings
import uuid
from django.utils.text import slugify
from django.db.models.signals import post_save
from django.dispatch import receiver
# from dashboard.models import UserProfile

class CustomUserManager(BaseUserManager):
    def create_user(self, email, name, password=None, **extra_fields):
        if not email:
            raise ValueError(_("Email address must be provided"))
        email = self.normalize_email(email)
        user = self.model(email=email, name=name, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))

        return self.create_user(email, name, password, **extra_fields)

class CustomUser(AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username = models.CharField(
        _("Username"),
        max_length=150,
        unique=True,
        blank=True,
        null=True
    )
    first_name = models.CharField(_("First Name"), max_length=30, blank=True)
    last_name = models.CharField(_("Last Name"), max_length=150, blank=True)
    name = models.CharField(_("Full Name"), max_length=255)
    email = models.EmailField(_("Email Address"), unique=True, max_length=255)
    mobile_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message=_("Mobile number must be in the format: '+999999999'. Up to 15 digits allowed.")
    )
    mobile = models.CharField(_("Mobile Number"), validators=[mobile_regex], max_length=17, blank=True, null=True, unique=True)
    profile_image = models.ImageField(_("Profile Picture"), upload_to='profile_images/', null=True, blank=True)
    
    is_staff = models.BooleanField(_("Staff Status"), default=False)
    is_active = models.BooleanField(_("Active"), default=True)
    is_email_verified = models.BooleanField(_("Email Verified"), default=False)
    date_joined = models.DateTimeField(_("Date Joined"), default=timezone.now)
    last_login = models.DateTimeField(_("Last Login"), blank=True, null=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    class Meta:
        verbose_name = _("User")
        verbose_name_plural = _("Users")
        ordering = ['-date_joined']

    def __str__(self):
        return self.email

    def get_full_name(self):
        return self.name

    def get_short_name(self):
        return self.first_name

    def save(self, *args, **kwargs):
        if not self.username:
            base_username = slugify(self.name) if self.name else self.email.split('@')[0]
            username = base_username
            while CustomUser.objects.filter(username=username).exists():
                username = f"{base_username}_{uuid.uuid4().hex[:8]}"
            self.username = username
        if not self.name:
            self.name = f"{self.first_name} {self.last_name}".strip()
        super().save(*args, **kwargs)

    @property
    def profile(self):
        # Use lazy loading
        from dashboard.models import UserProfile
        return UserProfile.objects.get_or_create(user=self)[0]

# Change the signal function
@receiver(post_save, sender=CustomUser)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    from dashboard.models import UserProfile
    if created:
        UserProfile.objects.create(user=instance)
    else:
        UserProfile.objects.get_or_create(user=instance)[0].save()

class LoginHistory(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='login_history')
    login_datetime = models.DateTimeField(_("Login Time"), auto_now_add=True)
    ip_address = models.GenericIPAddressField(_("IP Address"))
    user_agent = models.TextField(_("User Agent"))

    class Meta:
        verbose_name = _("Login History")
        verbose_name_plural = _("Login Histories")
        ordering = ['-login_datetime']

    def __str__(self):
        return f"{self.user.email} - {self.login_datetime}"
