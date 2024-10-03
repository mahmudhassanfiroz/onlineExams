from django.contrib import admin
from .models import ExamCategory, Batch, Question, ExamSchedule, ExamRegistration, ExamResult, ExamSettings, UserPerformance, MockExam, UserAnswer

@admin.register(ExamCategory)
class ExamCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)

@admin.register(Batch)
class BatchAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'start_date', 'end_date', 'time')
    list_filter = ('category', 'start_date')
    search_fields = ('name', 'category__name')

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('question_text', 'category', 'question_type')
    list_filter = ('category', 'question_type')
    search_fields = ('question_text', 'category__name')

@admin.register(ExamSchedule)
class ExamScheduleAdmin(admin.ModelAdmin):
    list_display = ('batch', 'exam_date', 'duration')
    list_filter = ('batch__category', 'exam_date')
    search_fields = ('batch__name',)

@admin.register(ExamRegistration)
class ExamRegistrationAdmin(admin.ModelAdmin):
    list_display = ('user', 'exam', 'registration_date', 'payment_status')
    list_filter = ('payment_status', 'registration_date')
    search_fields = ('user__username', 'exam__batch__name')

@admin.register(ExamResult)
class ExamResultAdmin(admin.ModelAdmin):
    list_display = ('registration', 'score', 'submitted_at')
    list_filter = ('submitted_at',)
    search_fields = ('registration__user__username', 'registration__exam__batch__name')

@admin.register(ExamSettings)
class ExamSettingsAdmin(admin.ModelAdmin):
    list_display = ('exam', 'time_limit', 'pass_mark', 'total_questions')
    search_fields = ('exam__batch__name',)

@admin.register(UserPerformance)
class UserPerformanceAdmin(admin.ModelAdmin):
    list_display = ('user', 'exam_category', 'total_exams', 'average_score', 'last_exam_date')
    list_filter = ('exam_category', 'last_exam_date')
    search_fields = ('user__username', 'exam_category__name')

@admin.register(MockExam)
class MockExamAdmin(admin.ModelAdmin):
    list_display = ('user', 'exam_category', 'start_time', 'end_time', 'score')
    list_filter = ('exam_category', 'start_time')
    search_fields = ('user__username', 'exam_category__name')

@admin.register(UserAnswer)
class UserAnswerAdmin(admin.ModelAdmin):
    list_display = ('user', 'question', 'exam_registration', 'is_correct')
    list_filter = ('is_correct', 'exam_registration__exam__batch__category')
    search_fields = ('user__username', 'question__question_text')

