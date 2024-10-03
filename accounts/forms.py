from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, AuthenticationForm, PasswordResetForm, SetPasswordForm
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from accounts.models import CustomUser
from dashboard.models import UserProfile

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(
        label=_("ইমেইল"),
        max_length=254,
        widget=forms.EmailInput(attrs={'autocomplete': 'email'})
    )
    
    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ('email', 'name', 'mobile')

    def clean_email(self):
        email = self.cleaned_data['email']
        if CustomUser.objects.filter(email=email).exists():
            raise ValidationError(_("এই ইমেইল ঠিকানা দিয়ে ইতিমধ্যে একটি অ্যাকাউন্ট রয়েছে।"))
        return email

    def clean_mobile(self):
        mobile = self.cleaned_data['mobile']
        if mobile and CustomUser.objects.filter(mobile=mobile).exists():
            raise ValidationError(_("এই মোবাইল নম্বর দিয়ে ইতিমধ্যে একটি অ্যাকাউন্ট রয়েছে।"))
        return mobile

class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = ('email', 'name', 'mobile', 'profile_image')

class CustomAuthenticationForm(AuthenticationForm):
    username = forms.EmailField(label=_("ইমেইল"), widget=forms.TextInput(attrs={'autofocus': True}))

class CustomPasswordResetForm(PasswordResetForm):
    email = forms.EmailField(
        label=_("ইমেইল"),
        max_length=254,
        widget=forms.EmailInput(attrs={'autocomplete': 'email'})
    )

class CustomSetPasswordForm(SetPasswordForm):
    new_password1 = forms.CharField(
        label=_("নতুন পাসওয়ার্ড"),
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}),
        strip=False,
    )
    new_password2 = forms.CharField(
        label=_("নতুন পাসওয়ার্ড নিশ্চিত করুন"),
        strip=False,
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}),
    )

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ('bio', 'birth_date', 'location', 'website')
        widgets = {
            'birth_date': forms.DateInput(attrs={'type': 'date'}),
        }

class EmailVerificationForm(forms.Form):
    code = forms.CharField(label=_("যাচাইকরণ কোড"), max_length=6, min_length=6)

class PasswordStrengthForm(forms.Form):
    password = forms.CharField(
        label=_("পাসওয়ার্ড"),
        widget=forms.PasswordInput(attrs={'id': 'password-strength-input'})
    )

    def clean_password(self):
        password = self.cleaned_data['password']
        if len(password) < 8:
            raise ValidationError(_("পাসওয়ার্ড অবশ্যই কমপক্ষে ৮ অক্ষরের হতে হবে।"))
        if not any(char.isdigit() for char in password):
            raise ValidationError(_("পাসওয়ার্ডে অবশ্যই কমপক্ষে একটি সংখ্যা থাকতে হবে।"))
        if not any(char.isupper() for char in password):
            raise ValidationError(_("পাসওয়ার্ডে অবশ্যই কমপক্ষে একটি বড় হাতের অক্ষর থাকতে হবে।"))
        if not any(char.islower() for char in password):
            raise ValidationError(_("পাসওয়ার্ডে অবশ্যই কমপক্ষে একটি ছোট হাতের অক্ষর থাকতে হবে।"))
        if not any(char in "!@#$%^&*()_+-=[]{}|;:,.<>?" for char in password):
            raise ValidationError(_("পাসওয়ার্ডে অবশ্যই কমপক্ষে একটি বিশেষ চিহ্ন থাকতে হবে।"))
        return password

class AccountSettingsForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['email', 'username', 'first_name', 'last_name']

