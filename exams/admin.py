from django.contrib import admin
from .models import Question, Exam, UserExam, UserAnswer

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('question_text_short', 'exam_category', 'question_type', 'marks', 'difficulty_level')
    list_filter = ('exam_category', 'question_type', 'difficulty_level')
    search_fields = ('question_text', 'tags')
    
    def question_text_short(self, obj):
        return obj.question_text[:50]
    question_text_short.short_description = 'প্রশ্ন'

@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = ('title', 'exam_category', 'duration', 'total_marks', 'pass_marks', 'is_free', 'price')
    list_filter = ('exam_category', 'is_free')
    search_fields = ('title', 'description')
    prepopulated_fields = {'slug': ('title',)}
    filter_horizontal = ('questions',)

@admin.register(UserExam)
class UserExamAdmin(admin.ModelAdmin):
    list_display = ('user', 'exam', 'start_time', 'end_time', 'score', 'is_completed')
    list_filter = ('is_completed', 'exam__exam_category')
    search_fields = ('user__username', 'exam__title')
    date_hierarchy = 'start_time'

@admin.register(UserAnswer)
class UserAnswerAdmin(admin.ModelAdmin):
    list_display = ('user_exam', 'question_short', 'is_correct')
    list_filter = ('is_correct', 'user_exam__exam')
    search_fields = ('user_exam__user__username', 'question__question_text')
    
    def question_short(self, obj):
        return obj.question.question_text[:50]
    question_short.short_description = 'প্রশ্ন'

