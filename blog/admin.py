from django.contrib import admin
from django.utils.html import format_html
from .models import Tag, Post, Comment, Subscription, Reaction

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'post_count')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)

    def post_count(self, obj):
        return obj.post_set.count()
    post_count.short_description = 'পোস্ট সংখ্যা'

class CommentInline(admin.TabularInline):
    model = Comment
    extra = 0

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'created_at', 'is_featured', 'views', 'comment_count', 'reaction_count', 'status')
    list_filter = ('tags', 'is_featured', 'created_at', 'status')
    search_fields = ('title', 'content', 'author__username')
    prepopulated_fields = {'slug': ('title',)}
    filter_horizontal = ('tags',)
    readonly_fields = ('views', 'created_at', 'updated_at')
    inlines = [CommentInline]
    actions = ['make_featured', 'remove_featured', 'publish_posts', 'unpublish_posts']

    def comment_count(self, obj):
        return obj.comments.count()
    comment_count.short_description = 'মন্তব্য সংখ্যা'

    def reaction_count(self, obj):
        return obj.reactions.count()
    reaction_count.short_description = 'প্রতিক্রিয়া সংখ্যা'

    def make_featured(self, request, queryset):
        queryset.update(is_featured=True)
    make_featured.short_description = "নির্বাচিত পোস্টগুলি ফিচার্ড করুন"

    def remove_featured(self, request, queryset):
        queryset.update(is_featured=False)
    remove_featured.short_description = "নির্বাচিত পোস্টগুলি ফিচার্ড থেকে সরান"

    def publish_posts(self, request, queryset):
        queryset.update(status='published')
    publish_posts.short_description = "নির্বাচিত পোস্টগুলি প্রকাশ করুন"

    def unpublish_posts(self, request, queryset):
        queryset.update(status='draft')
    unpublish_posts.short_description = "নির্বাচিত পোস্টগুলি অপ্রকাশিত করুন"

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('user', 'post', 'short_content', 'created_at', 'is_approved')
    list_filter = ('is_approved', 'created_at')
    search_fields = ('user__username', 'post__title', 'content')
    actions = ['approve_comments', 'unapprove_comments']

    def short_content(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    short_content.short_description = 'মন্তব্য'

    def approve_comments(self, request, queryset):
        queryset.update(is_approved=True)
    approve_comments.short_description = "নির্বাচিত মন্তব্যগুলি অনুমোদন করুন"

    def unapprove_comments(self, request, queryset):
        queryset.update(is_approved=False)
    unapprove_comments.short_description = "নির্বাচিত মন্তব্যগুলি অননুমোদন করুন"

@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('email', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('email',)
    actions = ['activate_subscriptions', 'deactivate_subscriptions']

    def activate_subscriptions(self, request, queryset):
        queryset.update(is_active=True)
    activate_subscriptions.short_description = "নির্বাচিত সাবস্ক্রিপশনগুলি সক্রিয় করুন"

    def deactivate_subscriptions(self, request, queryset):
        queryset.update(is_active=False)
    deactivate_subscriptions.short_description = "নির্বাচিত সাবস্ক্রিপশনগুলি নিষ্ক্রিয় করুন"

@admin.register(Reaction)
class ReactionAdmin(admin.ModelAdmin):
    list_display = ('user', 'post', 'reaction_type', 'colored_reaction')
    list_filter = ('reaction_type',)
    search_fields = ('user__username', 'post__title')

    def colored_reaction(self, obj):
        colors = {
            'like': 'blue',
            'love': 'red',
            'haha': 'orange',
            'wow': 'green',
            'sad': 'purple',
            'angry': 'brown'
        }
        return format_html(
            '<span style="color: {};">{}</span>',
            colors.get(obj.reaction_type, 'black'),
            obj.get_reaction_type_display()
        )
    colored_reaction.short_description = 'রঙিন প্রতিক্রিয়া'

