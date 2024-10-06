from django.contrib import admin
from .models import Notification, NotificationPreference, NotificationDevice, NotificationLog

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'notification_type', 'title', 'is_read', 'created_at')
    list_filter = ('notification_type', 'is_read', 'created_at')
    search_fields = ('user__username', 'title', 'message')
    readonly_fields = ('created_at',)

@admin.register(NotificationPreference)
class NotificationPreferenceAdmin(admin.ModelAdmin):
    list_display = ('user', 'live_exam', 'exam_result', 'blog_post', 'book_purchase', 'general_info', 'upcoming_exam', 'login', 'package_purchase')
    list_filter = ('live_exam', 'exam_result', 'blog_post', 'book_purchase', 'general_info', 'upcoming_exam', 'login', 'package_purchase')
    search_fields = ('user__username',)

@admin.register(NotificationDevice)
class NotificationDeviceAdmin(admin.ModelAdmin):
    list_display = ('user', 'device_type', 'is_active')
    list_filter = ('device_type', 'is_active')
    search_fields = ('user__username', 'device_token')

@admin.register(NotificationLog)
class NotificationLogAdmin(admin.ModelAdmin):
    list_display = ('notification', 'sent_at', 'is_delivered', 'delivered_at')
    list_filter = ('is_delivered', 'sent_at', 'delivered_at')
    search_fields = ('notification__title', 'notification__user__username')
    readonly_fields = ('sent_at',)

