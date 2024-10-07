from django import forms
from django.utils.translation import gettext_lazy as _
from .models import UserPreference

class DashboardCustomizationForm(forms.ModelForm):
    class Meta:
        model = UserPreference
        fields = ['dashboard_layout', 'color_scheme', 'widget_order']

    dashboard_layout = forms.ChoiceField(
        choices=UserPreference.LAYOUT_CHOICES,
        widget=forms.RadioSelect,
        label=_("ড্যাশবোর্ড লেআউট")
    )

    color_scheme = forms.ChoiceField(
        choices=UserPreference.COLOR_SCHEME_CHOICES,
        widget=forms.RadioSelect,
        label=_("কালার স্কিম")
    )

    WIDGET_CHOICES = [
        ('recent_activity', _('সাম্প্রতিক কার্যক্রম')),
        ('upcoming_exams', _('আসন্ন পরীক্ষা')),
        ('performance_metrics', _('পারফরম্যান্স মেট্রিক্স')),
        ('notifications', _('বিজ্ঞপ্তি')),
        ('quick_links', _('দ্রুত লিঙ্ক')),
    ]

    widget_order = forms.MultipleChoiceField(
        choices=WIDGET_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label=_("উইজেট অর্ডার")
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.widget_order:
            self.fields['widget_order'].initial = self.instance.widget_order

    def clean_widget_order(self):
        widget_order = self.cleaned_data.get('widget_order')
        if not widget_order:
            raise forms.ValidationError(_("কমপক্ষে একটি উইজেট নির্বাচন করুন।"))
        return widget_order

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.widget_order = self.cleaned_data.get('widget_order')
        if commit:
            instance.save()
        return instance

