from django.contrib import admin
from .models import Category, Author, Book, Wishlist

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'category', 'price', 'is_featured')
    list_filter = ('category', 'is_featured')
    search_fields = ('title', 'author__name')

# @admin.register(Review)
# class ReviewAdmin(admin.ModelAdmin):
#     list_display = ('book', 'user', 'rating', 'created_at')
#     list_filter = ('rating',)
#     search_fields = ('book__title', 'user__username')

@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ('user', 'book', 'added_at')
    search_fields = ('user__username', 'book__title')

