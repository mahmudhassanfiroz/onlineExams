from django.db import models
from accounts.models import CustomUser
from liveExam.models import LiveExam, UserLiveExam
from django_ckeditor_5.fields import CKEditor5Field
from exams.models import Exam, UserExam
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

class Result(models.Model):
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, db_index=True)
    object_id = models.PositiveIntegerField(db_index=True)
    content_object = GenericForeignKey('content_type', 'object_id')
    
    score = models.FloatField()
    correct_answers = models.PositiveIntegerField()
    wrong_answers = models.PositiveIntegerField()
    total_questions = models.PositiveIntegerField()
    submission_time = models.DateTimeField(auto_now_add=True)
    
    def calculate_percentage(self):
        if isinstance(self.content_object, UserLiveExam):
            total_marks = self.content_object.live_exam.total_marks
        elif isinstance(self.content_object, UserExam):
            total_marks = self.content_object.exam.total_marks
        else:
            return 0
        
        return (self.score / total_marks) * 100 if total_marks > 0 else 0

    def __str__(self):
        if isinstance(self.content_object, UserLiveExam):
            return f"{self.content_object.user.username}'s result for live exam {self.content_object.live_exam.title}"
        elif isinstance(self.content_object, UserExam):
            return f"{self.content_object.user.username}'s result for exam {self.content_object.exam.title}"
        else:
            return f"Result {self.id}"
    
    class Meta:
        indexes = [
            models.Index(fields=['content_type', 'object_id']),
        ]



class Feedback(models.Model):
    result = models.ForeignKey(Result, on_delete=models.CASCADE)
    comment = CKEditor5Field()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Feedback for {self.result}"

class Leaderboard(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    live_exam = models.ForeignKey(LiveExam, on_delete=models.CASCADE)
    score = models.FloatField()
    rank = models.PositiveIntegerField()

    class Meta:
        unique_together = ('user', 'live_exam')

    def __str__(self):
        return f"{self.user.username}'s rank for {self.live_exam.title}"
