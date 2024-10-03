from django.db import models
from django.utils import timezone
from accounts.models import CustomUser
# from django_ckeditor_5.fields import CKEditor5Field

class LiveExam(models.Model):
    title = models.CharField(max_length=200)
    batch = models.ForeignKey('Batch', on_delete=models.CASCADE)
    exam_date = models.DateField(auto_now_add=True)
    start_time = models.TimeField()  # পরীক্ষা শুরুর সময়
    duration = models.DurationField()

    def is_today(self):
        return self.exam_date == timezone.now().date()

    def is_active(self):
        now = timezone.now()
        exam_start = timezone.make_aware(timezone.datetime.combine(self.exam_date, self.start_time))
        exam_end = exam_start + self.duration
        return exam_start <= now < exam_end

    def time_until_start(self):
        now = timezone.now()
        exam_start = timezone.make_aware(timezone.datetime.combine(self.exam_date, self.start_time))
        if now < exam_start:
            return exam_start - now
        return timezone.timedelta()

    def has_started(self):
        now = timezone.now()
        exam_start = timezone.make_aware(timezone.datetime.combine(self.exam_date, self.start_time))
        return now >= exam_start

    def is_upcoming(self):
        now = timezone.now()
        exam_start = timezone.make_aware(timezone.datetime.combine(self.exam_date, self.start_time))
        return now < exam_start <= (now + timezone.timedelta(days=1))

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

class Batch(models.Model):
    name = models.CharField(max_length=100)

class ExamSession(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='exam_sessions')
    exam = models.ForeignKey('LiveExam', on_delete=models.CASCADE, related_name='sessions')
    start_time = models.DateTimeField(default=timezone.now)
    end_time = models.DateTimeField(null=True, blank=True)
    is_completed = models.BooleanField(default=False)
    score = models.FloatField(null=True, blank=True)
    correct_answers = models.IntegerField(default=0)
    total_marks = models.FloatField(default=0)

    def __str__(self):
        return f"{self.user.username} - {self.exam.title} - {self.start_time}"

    def duration(self):
        if self.end_time:
            return self.end_time - self.start_time
        return None

    def is_time_up(self):
        return timezone.now() > (self.start_time + self.exam.duration)

    def remaining_time(self):
        if not self.is_completed and not self.is_time_up():
            return (self.start_time + self.exam.duration) - timezone.now()
        return timezone.timedelta()

    class Meta:
        unique_together = ['user', 'exam']
        ordering = ['-start_time']

