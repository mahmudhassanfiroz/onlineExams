from django.contrib import admin
from .models import Result, Feedback, Leaderboard

@admin.register(Result)
class ResultAdmin(admin.ModelAdmin):
    list_display = ('user', 'exam', 'score', 'submission_time')
    list_filter = ('exam', 'submission_time')
    search_fields = ('user__username', 'exam__title')

@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('result', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('result__user__username', 'comment')

@admin.register(Leaderboard)
class LeaderboardAdmin(admin.ModelAdmin):
    list_display = ('user', 'exam', 'score', 'rank')
    list_filter = ('exam',)
    search_fields = ('user__username', 'exam__title')

