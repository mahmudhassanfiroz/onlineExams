from django import forms
from .models import FooterContent
import json

class FooterContentForm(forms.ModelForm):
    class Meta:
        model = FooterContent
        fields = '__all__'

    def clean_quick_links(self):
        quick_links = self.cleaned_data.get('quick_links')
        if quick_links:
            try:
                json_data = json.loads(quick_links)
                if not isinstance(json_data, list):
                    raise forms.ValidationError("Quick links must be a JSON array.")
                for item in json_data:
                    if not isinstance(item, dict) or 'name' not in item or 'url' not in item:
                        raise forms.ValidationError("Each quick link must be an object with 'name' and 'url' keys.")
            except json.JSONDecodeError:
                raise forms.ValidationError("Invalid JSON format. Please enter a valid JSON array.")
        return quick_links

    def clean(self):
        cleaned_data = super().clean()
        # এখানে আপনি অতিরিক্ত ফর্ম-লেভেল ভ্যালিডেশন যোগ করতে পারেন
        return cleaned_data


class ContactForm(forms.Form):
    name = forms.CharField(label='আপনার নাম', max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(label='ইমেইল ঠিকানা', widget=forms.EmailInput(attrs={'class': 'form-control'}))
    subject = forms.CharField(label='বিষয়', max_length=200, widget=forms.TextInput(attrs={'class': 'form-control'}))
    message = forms.CharField(label='আপনার বার্তা', widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 5}))

