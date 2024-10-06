from django.contrib import admin
from .models import Payment, PackagePurchase, BookPurchase, Discount, Refund

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('user', 'amount', 'payment_type', 'status', 'created_at')
    list_filter = ('payment_type', 'status')
    search_fields = ('user__username', 'tran_id')
    readonly_fields = ('created_at', 'updated_at')

@admin.register(PackagePurchase)
class PackagePurchaseAdmin(admin.ModelAdmin):
    list_display = ('user', 'package', 'purchase_date', 'expiry_date')
    list_filter = ('package',)
    search_fields = ('user__username', 'package__name')

@admin.register(BookPurchase)
class BookPurchaseAdmin(admin.ModelAdmin):
    list_display = ('user', 'book', 'purchase_date')
    list_filter = ('book',)
    search_fields = ('user__username', 'book__title')

@admin.register(Discount)
class DiscountAdmin(admin.ModelAdmin):
    list_display = ('code', 'amount', 'is_percentage', 'is_active', 'valid_from', 'valid_to')
    list_filter = ('is_active', 'is_percentage')
    search_fields = ('code', 'description')

@admin.register(Refund)
class RefundAdmin(admin.ModelAdmin):
    list_display = ('payment', 'status', 'requested_at', 'processed_at')
    list_filter = ('status',)
    search_fields = ('payment__user__username', 'payment__tran_id')
    readonly_fields = ('requested_at',)

    def get_readonly_fields(self, request, obj=None):
        if obj and obj.status != 'PENDING':
            return self.readonly_fields + ('status', 'processed_at', 'refunded_amount')
        return self.readonly_fields

