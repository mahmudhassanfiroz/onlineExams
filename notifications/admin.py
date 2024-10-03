
from django.contrib import admin
from .models import Notification

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'notification_type', 'title', 'is_read', 'created_at')
    list_filter = ('notification_type', 'is_read', 'created_at')
    search_fields = ('user__username', 'title', 'message')
    readonly_fields = ('created_at',)
    
    fieldsets = (
        ('বেসিক তথ্য', {
            'fields': ('user', 'notification_type', 'title', 'message')
        }),
        ('অতিরিক্ত তথ্য', {
            'fields': ('is_read', 'created_at', 'content_type', 'object_id')
        }),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'content_type')

    def has_add_permission(self, request):
        return False  # নোটিফিকেশন ম্যানুয়ালি যোগ করা নিষিদ্ধ করা হয়েছে
