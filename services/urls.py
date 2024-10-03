
from django.urls import path
from . import views

app_name = 'services'

urlpatterns = [
    # সার্ভিস ক্যাটাগরি
    path('categories/', views.service_category_list, name='category_list'),
    path('category/<slug:category_slug>/', views.service_category_detail, name='category_detail'),
    
    # সার্ভিস
    path('service/<slug:category_slug>/<slug:service_slug>/', views.service_detail, name='service_detail'),
    path('service/<slug:slug>/register/', views.service_registration, name='service_registration'),
    
    # রিভিউ
    path('service/<slug:category_slug>/<slug:service_slug>/review/', views.add_review, name='add_review'),
    
    # প্রমোশন
    path('promotions/', views.promotions, name='promotions'),
    
    
    # FAQ
    path('service/<slug:slug>/faq/', views.service_faq, name='service_faq'),    
    # লাইভ চ্যাট (এটি একটি উদাহরণ, আপনার প্রয়োজন অনুযায়ী পরিবর্তন করুন)
    # path('live-chat/', views.live_chat, name='live_chat'),
]

