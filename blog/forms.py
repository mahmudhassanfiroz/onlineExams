from django import forms
from .models import Post, Comment, Subscription, Tag
from django_select2 import forms as s2forms
from tinymce.widgets import TinyMCE

class PostForm(forms.ModelForm):
    tags = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'কমা দিয়ে ট্যাগ আলাদা করুন'
    }))

    class Meta:
        model = Post
        fields = ['title', 'content', 'tags', 'status', 'image']
        widgets = {
            'content': TinyMCE(attrs={'cols': 80, 'rows': 30}),
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'পোস্টের শিরোনাম লিখুন'}),
            # 'category': forms.Select(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields['tags'].initial = ', '.join([tag.name for tag in self.instance.tags.all()])

    def save(self, commit=True):
        instance = super().save(commit=False)
        if commit:
            instance.save()
            
            # ট্যাগ সেভ করা
            tag_names = [tag.strip() for tag in self.cleaned_data['tags'].split(',') if tag.strip()]
            instance.tags.clear()
            for tag_name in tag_names:
                tag, created = Tag.objects.get_or_create(name=tag_name)
                instance.tags.add(tag)
        
        return instance

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']

class SubscriptionForm(forms.ModelForm):
    class Meta:
        model = Subscription
        fields = ['email']

