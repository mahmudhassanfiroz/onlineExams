from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.core.mail import send_mail
from django.conf import settings
from django.utils.crypto import get_random_string
from .forms import (
    AccountSettingsForm, CustomUserCreationForm, CustomAuthenticationForm,
    CustomPasswordResetForm, CustomSetPasswordForm, EmailVerificationForm, PasswordStrengthForm
)
from .models import CustomUser, LoginHistory


def register(request):
    form = CustomUserCreationForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save(commit=False)
        user.is_active = False
        user.save()
        send_verification_email(user)
        messages.success(request, _('Registration successful. Please verify your email.'))
        return redirect('accounts:login')
    return render(request, 'accounts/register.html', {'form': form})


def user_login(request):
    form = CustomAuthenticationForm(request, data=request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.get_user()
        login(request, user)
        LoginHistory.objects.create(
            user=user,
            ip_address=request.META.get('REMOTE_ADDR', ''),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )
        messages.success(request, _('Successfully logged in.'))
        return redirect('dashboard:dashboard')
    return render(request, 'accounts/login.html', {'form': form})


@login_required
def user_logout(request):
    logout(request)
    messages.success(request, _('Successfully logged out.'))
    return redirect('accounts:login')


def password_reset(request):
    form = CustomPasswordResetForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save(
            request=request,
            use_https=request.is_secure(),
            subject_template_name='accounts/password_reset_subject.txt',
            email_template_name='accounts/password_reset_email.html',
        )
        messages.success(request, _('Password reset link sent to your email.'))
        return redirect('accounts:login')
    return render(request, 'accounts/password_reset.html', {'form': form})


def password_reset_confirm(request, uidb64, token):
    form = CustomSetPasswordForm(request.user, request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, _('Password successfully updated.'))
        return redirect('accounts:login')
    return render(request, 'accounts/password_reset_confirm.html', {'form': form})


def verify_email(request):
    form = EmailVerificationForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        code = form.cleaned_data['code']
        user = CustomUser.objects.filter(verification_code=code, is_active=False).first()
        if user:
            user.is_active = True
            user.is_email_verified = True
            user.verification_code = ''
            user.save()
            messages.success(request, _('Email successfully verified. You can now log in.'))
            return redirect('accounts:login')
        messages.error(request, _('Invalid verification code.'))
    return render(request, 'accounts/verify_email.html', {'form': form})


@login_required
def change_password(request):
    form = PasswordStrengthForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        request.user.set_password(form.cleaned_data['password'])
        request.user.save()
        messages.success(request, _('Password successfully updated.'))
        return redirect('accounts:login')
    return render(request, 'accounts/change_password.html', {'form': form})


@login_required
def login_history(request):
    history = LoginHistory.objects.filter(user=request.user).only('login_datetime', 'ip_address', 'user_agent')
    return render(request, 'accounts/login_history.html', {'history': history})


def send_verification_email(user):
    verification_code = get_random_string(length=6)
    user.verification_code = verification_code
    user.save(update_fields=['verification_code'])

    subject = _('Email Verification')
    message = _(f'Your verification code is: {verification_code}')
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])


@login_required
def account_settings(request):
    form = AccountSettingsForm(request.POST or None, instance=request.user)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, _('Account settings updated successfully.'))
        return redirect('accounts:account_settings')
    return render(request, 'accounts/account_settings.html', {'form': form})

