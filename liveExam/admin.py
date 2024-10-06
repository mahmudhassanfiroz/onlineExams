from django.contrib import admin
from .models import LiveExam, UserLiveExam, LiveExamAnswer

@admin.register(LiveExam)
class LiveExamAdmin(admin.ModelAdmin):
    list_display = ('title', 'exam_category', 'exam_date', 'start_time', 'duration', 'total_marks', 'pass_marks', 'is_free', 'price', 'status')
    list_filter = ('exam_category', 'exam_date', 'is_free')
    search_fields = ('title', 'description')
    prepopulated_fields = {'slug': ('title',)}
    filter_horizontal = ('questions',)
    date_hierarchy = 'exam_date'

    def status(self, obj):
        return obj.status()
    status.short_description = 'অবস্থা'

@admin.register(UserLiveExam)
class UserLiveExamAdmin(admin.ModelAdmin):
    list_display = ('user', 'live_exam', 'start_time', 'end_time', 'score', 'is_completed')
    list_filter = ('is_completed', 'live_exam__exam_category')
    search_fields = ('user__username', 'live_exam__title')
    date_hierarchy = 'start_time'

@admin.register(LiveExamAnswer)
class LiveExamAnswerAdmin(admin.ModelAdmin):
    list_display = ('user_live_exam', 'question_short', 'is_correct')
    list_filter = ('is_correct', 'user_live_exam__live_exam')
    search_fields = ('user_live_exam__user__username', 'question__question_text')

    def question_short(self, obj):
        return obj.question.question_text[:50]
    question_short.short_description = 'প্রশ্ন'

