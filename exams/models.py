from django.db import models
from django.utils.text import slugify
from django_ckeditor_5.fields import CKEditor5Field
from accounts.models import CustomUser
from services.models import ExamCategory, Package
from django.contrib.postgres.fields import JSONField

class Question(models.Model):
    QUESTION_TYPES = (
        ('MCQ', 'বহুনির্বাচনী'),
        ('TF', 'সত্য/মিথ্যা'),
        ('SA', 'সংক্ষিপ্ত উত্তর'),
    )
    exam_category = models.ForeignKey(ExamCategory, on_delete=models.CASCADE, null=True, blank=True)
    question_text = CKEditor5Field()
    question_type = models.CharField(max_length=3, choices=QUESTION_TYPES)
    correct_answer = CKEditor5Field()
    marks = models.FloatField(default=1.0)
    difficulty_level = models.CharField(max_length=20, choices=[('EASY', 'সহজ'), ('MEDIUM', 'মাঝারি'), ('HARD', 'কঠিন')])
    tags = models.CharField(max_length=200, blank=True)  # কমা দিয়ে আলাদা করা ট্যাগ
    options = models.JSONField(blank=True, null=True)  # এখানে পরিবর্তন করা হয়েছে

    def __str__(self):
        return self.question_text[:50]
    def get_options(self):
           if self.question_type == 'MCQ':
               return self.options or []
           elif self.question_type == 'TF':
               return ['সত্য', 'মিথ্যা']
           else:
               return []

class Exam(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    exam_category = models.ForeignKey(ExamCategory, on_delete=models.CASCADE)
    description = CKEditor5Field()
    duration = models.DurationField()
    total_marks = models.FloatField()
    pass_marks = models.FloatField()
    is_free = models.BooleanField(default=False)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    questions = models.ManyToManyField(Question)
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

class UserExam(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)
    score = models.FloatField(null=True, blank=True)
    is_completed = models.BooleanField(default=False)

    def calculate_percentage(self):
        if self.score is not None and self.exam.total_marks > 0:
            return (self.score / self.exam.total_marks) * 100
        return 0

    def __str__(self):
        return f"{self.user.username} - {self.exam.title}"

class UserAnswer(models.Model):
    user_exam = models.ForeignKey(UserExam, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    answer_text = models.TextField()
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user_exam.user.username} - {self.question.question_text[:30]}"

