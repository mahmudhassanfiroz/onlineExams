import json
from django.contrib import admin
from django import forms
from .models import CTASection, CarouselSlide, FooterContent, MarqueeNotice, MenuItem, SiteSettings, AboutPage, AboutSection, AboutButton, ContactPage, ContactAdditionalInfo, Advertisement, QuickLink

@admin.register(MarqueeNotice)
class MarqueeNoticeAdmin(admin.ModelAdmin):
    list_display = ('message', 'is_active', 'start_date', 'end_date')
    list_filter = ('is_active', 'start_date', 'end_date')
    search_fields = ('message',)

@admin.register(CarouselSlide)
class CarouselSlideAdmin(admin.ModelAdmin):
    list_display = ('title', 'order', 'is_active')
    list_editable = ('order', 'is_active')
    search_fields = ('title', 'description')

@admin.register(CTASection)
class CTASectionAdmin(admin.ModelAdmin):
    list_display = ('title', 'button_text', 'is_active')
    list_editable = ('is_active',)

class FooterContentAdminForm(forms.ModelForm):
    def clean_quick_links(self):
        quick_links = self.cleaned_data.get('quick_links')
        try:
            json.loads(quick_links)
        except json.JSONDecodeError:
            raise forms.ValidationError("অবৈধ JSON ফরম্যাট। অনুগ্রহ করে একটি বৈধ JSON অ্যারে লিখুন।")
        return quick_links

class QuickLinkInline(admin.TabularInline):
    model = QuickLink
    extra = 1

@admin.register(FooterContent)
class FooterContentAdmin(admin.ModelAdmin):
    form = FooterContentAdminForm
    inlines = [QuickLinkInline]
    fieldsets = (
        ('যোগাযোগের তথ্য', {
            'fields': ('contact_title', 'email_label', 'phone_label', 'email', 'phone')
        }),
        ('দ্রুত লিঙ্ক', {
            'fields': ('quick_links_title',)
        }),
        ('সামাজিক মাধ্যম', {
            'fields': ('social_media_title', 'facebook_url', 'twitter_url', 'linkedin_url', 'instagram_url')
        }),
        ('কপিরাইট', {
            'fields': ('copyright_text',)
        }),
    )

    def has_add_permission(self, request):
        # শুধুমাত্র একটি ইনস্ট্যান্স অনুমোদন করুন
        return not FooterContent.objects.exists()

@admin.register(QuickLink)
class QuickLinkAdmin(admin.ModelAdmin):
    list_display = ('name', 'url', 'order')
    list_editable = ('order',)

@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'url', 'order', 'parent', 'get_children')
    list_editable = ('url', 'order')
    search_fields = ('name', 'url')
    list_filter = ('parent',)
    
    def get_children(self, obj):
        return ", ".join([child.name for child in obj.children.all()])
    get_children.short_description = 'Children'

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "parent":
            kwargs["queryset"] = MenuItem.objects.filter(parent__isnull=True)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    fieldsets = (
        ('সাইট তথ্য', {
            'fields': ('site_title', 'site_logo', 'navbar_title', 'favicon')
        }),
        ('হোমপেজ শিরোনাম', {
            'fields': ('home_service_packages_title', 'home_featured_packages_title', 
                       'home_testimonials_title', 'home_faq_title', 'home_dashboard_title', 
                       'home_next_exam_title', 'home_average_score_title', 'home_latest_result_title')
        }),
    )

    def has_add_permission(self, request):
        # শুধুমাত্র একটি ইনস্ট্যান্স অনুমোদন করুন
        return not SiteSettings.objects.exists()

class AboutSectionInline(admin.StackedInline):
    model = AboutSection
    extra = 1

class AboutButtonInline(admin.StackedInline):
    model = AboutButton

@admin.register(AboutPage)
class AboutPageAdmin(admin.ModelAdmin):
    inlines = [AboutSectionInline]

@admin.register(AboutSection)
class AboutSectionAdmin(admin.ModelAdmin):
    inlines = [AboutButtonInline]

class ContactAdditionalInfoInline(admin.StackedInline):
    model = ContactAdditionalInfo
    extra = 1

@admin.register(ContactPage)
class ContactPageAdmin(admin.ModelAdmin):
    inlines = [ContactAdditionalInfoInline]

@admin.register(Advertisement)
class AdvertisementAdmin(admin.ModelAdmin):
    list_display = ('title', 'position', 'is_active')
    list_filter = ('is_active', 'position')
    search_fields = ('title', 'content')

