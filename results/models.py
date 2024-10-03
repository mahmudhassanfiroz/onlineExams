from django.db import models
from accounts.models import CustomUser
from liveExam.models import LiveExam 
from django_ckeditor_5.fields import CKEditor5Field
class Result(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    exam = models.ForeignKey(LiveExam, on_delete=models.CASCADE)
    score = models.PositiveIntegerField()
    correct_answers = models.PositiveIntegerField()
    wrong_answers = models.PositiveIntegerField()
    total_questions = models.PositiveIntegerField()
    submission_time = models.DateTimeField(auto_now_add=True)

    def calculate_percentage(self):
        return (self.score / (self.total_questions * self.exam.marks_per_question)) * 100

class Feedback(models.Model):
    result = models.ForeignKey(Result, on_delete=models.CASCADE)
    comment = CKEditor5Field()
    created_at = models.DateTimeField(auto_now_add=True)

class Leaderboard(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    exam = models.ForeignKey(LiveExam, on_delete=models.CASCADE)
    score = models.PositiveIntegerField()
    rank = models.PositiveIntegerField()

