
from django.urls import path
from . import views

app_name = 'liveExam'

urlpatterns = [
    # লাইভ পরীক্ষা তালিকা
    path('', views.live_exam_list, name='live_exam_list'),
    path('exam/<int:exam_id>/', views.exam_detail, name='exam_detail'),

    # পরীক্ষা রেজিস্ট্রেশন
    # path('exam/<int:exam_id>/register/', views.exam_registration, name='exam_registration'),
    path('exam/<int:exam_id>/confirmation/', views.exam_confirmation, name='exam_confirmation'),

    # পরীক্ষা ইন্টারফেস
    path('exam/<int:exam_id>/start/', views.start_exam, name='start_exam'),
    path('exam/<int:exam_id>/submit/', views.submit_exam, name='submit_exam'),

    # ফলাফল এবং পারফরম্যান্স
    path('exam/<int:exam_id>/result/', views.exam_result, name='exam_result'),
    path('exam/<int:exam_id>/performance/', views.performance_review, name='performance_review'),

    path('exam/<int:exam_id>/status/', views.exam_status, name='exam_status'),

    # প্রশাসনিক কার্যক্রম
    # path('admin/create-exam/', views.create_exam, name='create_exam'),
    # path('admin/edit-exam/<int:exam_id>/', views.edit_exam, name='edit_exam'),
    # path('admin/create-question/<int:exam_id>/', views.create_question, name='create_question'),
    # path('admin/edit-question/<int:question_id>/', views.edit_question, name='edit_question'),
]
