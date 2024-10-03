from django.db import models
from accounts.models import CustomUser
from services.models import Service, Package
from django_ckeditor_5.fields import CKEditor5Field

class ExamCategory(models.Model):
    name = models.CharField(max_length=100)
    description = CKEditor5Field()
    service = models.ForeignKey(Service, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.name

class Batch(models.Model):
    name = models.CharField(max_length=100)
    category = models.ForeignKey('ExamCategory', on_delete=models.CASCADE, related_name='batches')
    start_date = models.DateField()
    end_date = models.DateField()
    time = models.TimeField()
    participants = models.ManyToManyField(CustomUser, related_name='batches', blank=True)

    def __str__(self):
        return f"{self.name} - {self.category.name}"

class Question(models.Model):
    QUESTION_TYPES = (
        ('MCQ', 'Multiple Choice'),
        ('TF', 'True/False'),
        ('SA', 'Short Answer'),
    )
    category = models.ForeignKey(ExamCategory, on_delete=models.CASCADE)
    question_text = CKEditor5Field()
    question_type = models.CharField(max_length=3, choices=QUESTION_TYPES)
    correct_answer = CKEditor5Field(max_length=555)
    
    def __str__(self):
        return self.question_text[:50]

class ExamSchedule(models.Model):
    batch = models.ForeignKey(Batch, on_delete=models.CASCADE)
    exam_date = models.DateTimeField(null=True, blank=True)
    duration = models.DurationField()

    def __str__(self):
        return f"Exam for {self.batch} on {self.exam_date}"

class ExamRegistration(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    exam = models.ForeignKey(ExamSchedule, on_delete=models.CASCADE)
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    package = models.ForeignKey(Package, on_delete=models.SET_NULL, null=True, blank=True)
    registration_date = models.DateTimeField(auto_now_add=True)
    payment_status = models.BooleanField(default=False)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.price:
            if self.package:
                self.price = self.package.price
            else:
                self.price = self.service.price
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username} - {self.exam}"

class ExamResult(models.Model):
    registration = models.OneToOneField(ExamRegistration, on_delete=models.CASCADE)
    score = models.IntegerField()
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Result for {self.registration}"

class ExamSettings(models.Model):
    exam = models.OneToOneField(ExamSchedule, on_delete=models.CASCADE)
    time_limit = models.DurationField()
    pass_mark = models.IntegerField()
    total_questions = models.IntegerField()

    def __str__(self):
        return f"Settings for {self.exam}"

class UserPerformance(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    exam_category = models.ForeignKey(ExamCategory, on_delete=models.CASCADE)
    total_exams = models.IntegerField(default=0)
    average_score = models.FloatField(default=0.0)
    last_exam_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Performance of {self.user.username} in {self.exam_category}"

class MockExam(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    exam_category = models.ForeignKey(ExamCategory, on_delete=models.CASCADE)
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)
    score = models.IntegerField(null=True, blank=True)
    questions = models.ManyToManyField(Question)

    def __str__(self):
        return f"Mock Exam by {self.user.username} for {self.exam_category}"

class UserAnswer(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    exam_registration = models.ForeignKey(ExamRegistration, on_delete=models.CASCADE)
    mock_exam = models.ForeignKey(MockExam, on_delete=models.CASCADE, null=True, blank=True)
    answer_text = CKEditor5Field()
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username}'s answer to {self.question}"

