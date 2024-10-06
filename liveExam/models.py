from django.db import models
from django.utils import timezone
from accounts.models import CustomUser
from services.models import ExamCategory
from exams.models import Question
from django.utils.text import slugify

class LiveExam(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    exam_category = models.ForeignKey(ExamCategory, on_delete=models.CASCADE, null=True)
    description = models.TextField()
    exam_date = models.DateField()
    start_time = models.TimeField()
    duration = models.DurationField()
    total_marks = models.FloatField()
    pass_marks = models.FloatField()
    questions = models.ManyToManyField(Question)
    is_free = models.BooleanField(default=False)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def is_active(self):
        now = timezone.now()
        exam_start = timezone.make_aware(timezone.datetime.combine(self.exam_date, self.start_time))
        exam_end = exam_start + self.duration
        return exam_start <= now < exam_end

    def status(self):
        now = timezone.now()
        exam_start = timezone.make_aware(timezone.datetime.combine(self.exam_date, self.start_time))
        exam_end = exam_start + self.duration

        if now < exam_start:
            return "আসন্ন"
        elif exam_start <= now < exam_end:
            return "চলমান"
        else:
            return "সমাপ্ত"

    def __str__(self):
        return self.title

class UserLiveExam(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    live_exam = models.ForeignKey(LiveExam, on_delete=models.CASCADE)
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)
    score = models.FloatField(null=True, blank=True)
    is_completed = models.BooleanField(default=False)

    def calculate_percentage(self):
        if self.score is not None and self.live_exam.total_marks > 0:
            return (self.score / self.live_exam.total_marks) * 100
        return 0

    def __str__(self):
        return f"{self.user.username} - {self.live_exam.title}"

class LiveExamAnswer(models.Model):
    user_live_exam = models.ForeignKey(UserLiveExam, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    answer_text = models.TextField()
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user_live_exam.user.username}'s answer to {self.question}"

