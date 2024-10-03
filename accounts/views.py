from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.core.mail import send_mail
from django.conf import settings
from django.utils.crypto import get_random_string
from .forms import (
    AccountSettingsForm, CustomUserCreationForm, CustomUserChangeForm, CustomAuthenticationForm,
    CustomPasswordResetForm, CustomSetPasswordForm, UserProfileForm,
    EmailVerificationForm, PasswordStrengthForm
)
from .models import CustomUser, LoginHistory


def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            # UserProfile.objects.create(user=user) এই লাইনটি মুছে ফেলুন, কারণ সিগন্যাল এটি করবে
            send_verification_email(user)
            messages.success(request, _('নিবন্ধন সফল হয়েছে। অনুগ্রহ করে আপনার ইমেইল যাচাই করুন।'))
            return redirect('accounts:login')
    else:
        form = CustomUserCreationForm()
    return render(request, 'accounts/register.html', {'form': form})


def user_login(request):
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            LoginHistory.objects.create(
                user=user,
                ip_address=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT')
            )
            messages.success(request, _('সফলভাবে লগইন হয়েছে।'))
            
            # এখানে প্রোফাইল বা ড্যাশবোর্ড পেজে রিডাইরেক্ট করা হচ্ছে
            return redirect('dashboard:dashboard')  # অথবা 'profile', যেটি আপনার প্রকল্পে ব্যবহৃত হচ্ছে
    else:
        form = CustomAuthenticationForm()
    return render(request, 'accounts/login.html', {'form': form})

@login_required
def user_logout(request):
    logout(request)
    messages.success(request, _('সফলভাবে লগআউট হয়েছে।'))
    return redirect('accounts:login')

def password_reset(request):
    if request.method == 'POST':
        form = CustomPasswordResetForm(request.POST)
        if form.is_valid():
            form.save(
                request=request,
                use_https=request.is_secure(),
                subject_template_name='accounts/password_reset_subject.txt',
                email_template_name='accounts/password_reset_email.html',
            )
            messages.success(request, _('পাসওয়ার্ড রিসেট লিংক আপনার ইমেইলে পাঠানো হয়েছে।'))
            return redirect('accounts:login')
    else:
        form = CustomPasswordResetForm()
    return render(request, 'accounts/password_reset.html', {'form': form})

def password_reset_confirm(request, uidb64, token):
    if request.method == 'POST':
        form = CustomSetPasswordForm(request.user, request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, _('আপনার পাসওয়ার্ড সফলভাবে পরিবর্তন করা হয়েছে।'))
            return redirect('accounts:login')
    else:
        form = CustomSetPasswordForm(request.user)
    return render(request, 'accounts/password_reset_confirm.html', {'form': form})

def verify_email(request):
    if request.method == 'POST':
        form = EmailVerificationForm(request.POST)
        if form.is_valid():
            code = form.cleaned_data['code']
            try:
                user = CustomUser.objects.get(verification_code=code, is_active=False)
                user.is_active = True
                user.is_email_verified = True
                user.verification_code = ''
                user.save()
                messages.success(request, _('আপনার ইমেইল সফলভাবে যাচাই করা হয়েছে। এখন আপনি লগইন করতে পারেন।'))
                return redirect('accounts:login')
            except CustomUser.DoesNotExist:
                messages.error(request, _('অবৈধ যাচাইকরণ কোড।'))
    else:
        form = EmailVerificationForm()
    return render(request, 'accounts/verify_email.html', {'form': form})

@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordStrengthForm(request.POST)
        if form.is_valid():
            request.user.set_password(form.cleaned_data['password'])
            request.user.save()
            messages.success(request, _('আপনার পাসওয়ার্ড সফলভাবে পরিবর্তন করা হয়েছে।'))
            return redirect('accounts:login')
    else:
        form = PasswordStrengthForm()
    return render(request, 'accounts/change_password.html', {'form': form})

@login_required
def login_history(request):
    history = LoginHistory.objects.filter(user=request.user).order_by('-login_datetime')
    return render(request, 'accounts/login_history.html', {'history': history})

def send_verification_email(user):
    verification_code = get_random_string(length=6)
    user.verification_code = verification_code
    user.save()

    subject = _('ইমেইল যাচাইকরণ')
    message = _(f'আপনার যাচাইকরণ কোড হল: {verification_code}')
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [user.email]
    
    send_mail(subject, message, from_email, recipient_list)

@login_required
def account_settings(request):
    if request.method == 'POST':
        form = AccountSettingsForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, _('আপনার অ্যাকাউন্ট সেটিংস সফলভাবে আপডেট করা হয়েছে।'))
            return redirect('accounts:account_settings')
    else:
        form = AccountSettingsForm(instance=request.user)
    
    return render(request, 'accounts/account_settings.html', {'form': form})

