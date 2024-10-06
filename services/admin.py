from django.contrib import admin
from .models import ExamCategory, Package, UserPackage

@admin.register(ExamCategory)
class ExamCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Package)
class PackageAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'duration', 'package_type', 'is_featured')
    list_filter = ('package_type', 'is_featured')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    filter_horizontal = ('exam_categories',)

@admin.register(UserPackage)
class UserPackageAdmin(admin.ModelAdmin):
    list_display = ('user', 'package', 'purchase_date', 'expiry_date', 'is_active')
    list_filter = ('is_active', 'package')
    search_fields = ('user__username', 'package__name')
    date_hierarchy = 'purchase_date'
