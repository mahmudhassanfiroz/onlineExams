# from click import Option
from django.contrib import admin

from exams.models import ExamResult, Question, UserAnswer
from .models import LiveExam, Batch

@admin.register(LiveExam)
class LiveExamAdmin(admin.ModelAdmin):
    list_display = ('title', 'batch', 'start_time', 'duration', 'is_active')
    list_filter = ('batch', 'start_time')
    search_fields = ('title', 'batch__name')

@admin.register(Batch)
class BatchAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

# @admin.register(UserProfile)
# class UserProfileAdmin(admin.ModelAdmin):
#     list_display = ('user', 'phone_number')
#     search_fields = ('user__username', 'phone_number')

# class OptionInline(admin.TabularInline):
#     model = Option
#     extra = 4

# @admin.register(Question)
# class QuestionAdmin(admin.ModelAdmin):
#     list_display = ('text', 'live_exam', 'marks')
#     list_filter = ('live_exam',)
#     search_fields = ('text',)
#     inlines = [OptionInline]

# @admin.register(ExamRegistration)
# class ExamRegistrationAdmin(admin.ModelAdmin):
#     list_display = ('user', 'live_exam', 'registration_time', 'is_paid')
#     list_filter = ('live_exam', 'is_paid')
#     search_fields = ('user__username', 'live_exam__title')


# @admin.register(ExamResult)
# class ExamResultAdmin(admin.ModelAdmin):
#     list_display = ('user', 'live_exam', 'score', 'submission_time')
#     list_filter = ('live_exam',)
#     search_fields = ('user__username', 'live_exam__title')

# @admin.register(UserAnswer)
# class UserAnswerAdmin(admin.ModelAdmin):
#     list_display = ('user', 'question', 'selected_option', 'is_correct')
#     list_filter = ('is_correct', 'question__live_exam')
#     search_fields = ('user__username', 'question__text')

# @admin.register(Notification)
# class NotificationAdmin(admin.ModelAdmin):
#     list_display = ('user', 'message', 'created_at', 'is_read')
#     list_filter = ('is_read', 'created_at')
#     search_fields = ('user__username', 'message')

# @admin.register(Payment)
# class PaymentAdmin(admin.ModelAdmin):
#     list_display = ('user', 'exam_registration', 'amount', 'payment_date', 'transaction_id')
#     list_filter = ('payment_date',)
#     search_fields = ('user__username', 'transaction_id')

# @admin.register(Leaderboard)
# class LeaderboardAdmin(admin.ModelAdmin):
#     list_display = ('live_exam', 'user', 'score', 'rank')
#     list_filter = ('live_exam',)
#     search_fields = ('user__username', 'live_exam__title')

