
from django import forms
from .models import ServiceRegistration, Review

class ServiceRegistrationForm(forms.ModelForm):
    class Meta:
        model = ServiceRegistration
        fields = ['package']

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.Select(choices=[(i, i) for i in range(1, 6)]),
            'comment': forms.Textarea(attrs={'rows': 4}),
        }
        labels = {
            'rating': 'রেটিং',
            'comment': 'মন্তব্য',
        }


