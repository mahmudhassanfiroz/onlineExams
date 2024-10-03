
from django import forms
from django.core.validators import RegexValidator

from exams.models import ExamRegistration
# from .models import ExamRegistration

class ExamRegistrationForm(forms.ModelForm):
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="ফোন নম্বর এই ফরম্যাটে হতে হবে: '+8801711111111'."
    )

    full_name = forms.CharField(
        label='পূর্ণ নাম',
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    email = forms.EmailField(
        label='ইমেইল',
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    phone_number = forms.CharField(
        label='ফোন নম্বর',
        validators=[phone_regex],
        max_length=17,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    institution = forms.CharField(
        label='প্রতিষ্ঠান',
        max_length=200,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    agreed_to_terms = forms.BooleanField(
        label='আমি সকল নিয়ম ও শর্তাবলী পড়েছি এবং সম্মত হয়েছি',
        required=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )

    class Meta:
        model = ExamRegistration
        fields = ['full_name', 'email', 'phone_number', 'institution', 'agreed_to_terms']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        exam = self.instance.exam
        if ExamRegistration.objects.filter(exam=exam, email=email).exists():
            raise forms.ValidationError("এই ইমেইল দিয়ে ইতিমধ্যে এই পরীক্ষার জন্য নিবন্ধন করা হয়েছে।")
        return email

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        exam = self.instance.exam
        if ExamRegistration.objects.filter(exam=exam, phone_number=phone_number).exists():
            raise forms.ValidationError("এই ফোন নম্বর দিয়ে ইতিমধ্যে এই পরীক্ষার জন্য নিবন্ধন করা হয়েছে।")
        return phone_number

