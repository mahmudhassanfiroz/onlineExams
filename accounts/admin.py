from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _

from dashboard.models import UserProfile
from .models import CustomUser, LoginHistory

class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = _('ব্যবহারকারী প্রোফাইল')

class LoginHistoryInline(admin.TabularInline):
    model = LoginHistory
    extra = 0
    readonly_fields = ('login_datetime', 'ip_address', 'user_agent')
    can_delete = False
    verbose_name_plural = _('লগইন ইতিহাস')
    max_num = 5

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('ব্যক্তিগত তথ্য'), {'fields': ('name', 'mobile')}),
        (_('অনুমতি'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        (_('গুরুত্বপূর্ণ তারিখ'), {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'name', 'mobile', 'password1', 'password2'),
        }),
    )
    list_display = ('email', 'name', 'mobile', 'is_staff', 'is_active')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups')
    search_fields = ('email', 'name', 'mobile')
    ordering = ('email',)
    inlines = (UserProfileInline, LoginHistoryInline)

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'birth_date', 'location')
    search_fields = ('user__email', 'user__name', 'location')
    list_filter = ('location',)

@admin.register(LoginHistory)
class LoginHistoryAdmin(admin.ModelAdmin):
    list_display = ('user', 'login_datetime', 'ip_address')
    list_filter = ('login_datetime',)
    search_fields = ('user__email', 'user__name', 'ip_address')
    readonly_fields = ('user', 'login_datetime', 'ip_address', 'user_agent')

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

