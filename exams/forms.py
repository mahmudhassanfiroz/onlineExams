
from django import forms
from .models import ExamRegistration, ExamSettings, Question

class ExamRegistrationForm(forms.ModelForm):
    class Meta:
        model = ExamRegistration
        fields = []  # ফর্মে কোনো ফিল্ড নেই, কারণ user এবং exam ভিউ থেকে সেট করা হবে

class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['question_text', 'question_type', 'correct_answer']

class ExamSettingsForm(forms.ModelForm):
    class Meta:
        model = ExamSettings
        fields = ['time_limit', 'pass_mark', 'total_questions']
        widgets = {
            'time_limit': forms.TimeInput(attrs={'type': 'time'}),
        }

