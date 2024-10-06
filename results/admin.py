from django.contrib import admin
from .models import Result, Feedback, Leaderboard

@admin.register(Result)
class ResultAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_user', 'get_exam_title', 'score', 'correct_answers', 'wrong_answers', 'total_questions', 'submission_time')
    list_filter = ('content_type', 'submission_time')
    search_fields = ('content_object__user__username', 'content_object__live_exam__title', 'content_object__exam__title')

    def get_user(self, obj):
        if hasattr(obj.content_object, 'user'):
            return obj.content_object.user.username
        return 'N/A'
    get_user.short_description = 'User'

    def get_exam_title(self, obj):
        if hasattr(obj.content_object, 'live_exam'):
            return obj.content_object.live_exam.title
        elif hasattr(obj.content_object, 'exam'):
            return obj.content_object.exam.title
        return 'N/A'
    get_exam_title.short_description = 'Exam Title'

@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_result', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('result__content_object__user__username', 'comment')

    def get_result(self, obj):
        return str(obj.result)
    get_result.short_description = 'Result'

@admin.register(Leaderboard)
class LeaderboardAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'live_exam', 'score', 'rank')
    list_filter = ('live_exam', 'rank')
    search_fields = ('user__username', 'live_exam__title')
