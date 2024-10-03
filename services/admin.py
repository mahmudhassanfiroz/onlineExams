from django.contrib import admin
from .models import ServiceCategory, Service, Package, ServiceRegistration, Promotion, Review, FAQ

@admin.register(ServiceCategory)
class ServiceCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price')
    list_filter = ('category',)
    search_fields = ('name', 'description')

class PackageInline(admin.TabularInline):
    model = Package
    extra = 1

@admin.register(Package)
class PackageAdmin(admin.ModelAdmin):
    list_display = ('name', 'service', 'price')
    list_filter = ('service',)
    search_fields = ('name',)

@admin.register(ServiceRegistration)
class ServiceRegistrationAdmin(admin.ModelAdmin):
    list_display = ('user', 'service', 'package', 'registration_date', 'payment_status')
    list_filter = ('service', 'payment_status', 'registration_date')
    search_fields = ('user__username', 'user__email', 'service__name')
    date_hierarchy = 'registration_date'

@admin.register(Promotion)
class PromotionAdmin(admin.ModelAdmin):
    list_display = ('code', 'service', 'discount_percent', 'valid_from', 'valid_to')
    list_filter = ('service', 'valid_from', 'valid_to')
    search_fields = ('code', 'service__name')

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('user', 'service', 'rating', 'created_at')
    list_filter = ('service', 'rating', 'created_at')
    search_fields = ('user__username', 'user__email', 'service__name', 'comment')
    date_hierarchy = 'created_at'

@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ('service', 'question')
    list_filter = ('service',)
    search_fields = ('service__name', 'question', 'answer')

