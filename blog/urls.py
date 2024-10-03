from django.urls import path
from . import views

app_name = 'blog'

urlpatterns = [
    # পোস্ট সম্পর্কিত URL
    path('', views.post_list, name='post_list'),
    path('post/<slug:slug>/', views.post_detail, name='post_detail'),
    path('create/', views.create_post, name='create_post'),
    path('edit/<slug:slug>/', views.edit_post, name='edit_post'),
    path('delete/<slug:slug>/', views.delete_post, name='delete_post'),
    
    # ইন্টারঅ্যাকশন সম্পর্কিত URL
    path('react/<slug:slug>/', views.react_to_post, name='react_to_post'),
    path('share/<slug:slug>/', views.share_post, name='share_post'),
    path('subscribe/', views.subscribe, name='subscribe'),
    
    # ফিল্টারিং এবং ন্যাভিগেশন সম্পর্কিত URL
    path('tag/<slug:tag_slug>/', views.post_list, name='tag_posts'),
    path('author/<str:username>/', views.author_posts, name='author_posts'),
    path('archive/<int:year>/<int:month>/', views.archive, name='archive'),
    
    # অতিরিক্ত পৃষ্ঠা
    path('tags/', views.tag_list, name='tag_list'),
]
