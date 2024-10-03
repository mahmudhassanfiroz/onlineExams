from django.urls import path
from . import views

app_name = 'exams'  # এটি নেমস্পেসিং এর জন্য ব্যবহৃত হয়

urlpatterns = [
    # বিদ্যমান URL প্যাটার্নগুলি
    path('categories/', views.exam_category_list, name='category_list'),
    path('category/<int:category_id>/', views.exam_category_detail, name='exam_category_detail'),
    path('register/<int:exam_id>/', views.exam_registration, name='exam_registration'),
    # path('take-exam/<int:exam_id>/', views.take_exam, name='take_exam'),
    # path('result/<int:result_id>/', views.exam_result, name='exam_result'),
    path('exam-history/', views.exam_history, name='exam_history'),
    path('batch/<int:batch_id>/', views.batch_detail, name='batch_detail'),

    # নতুন URL প্যাটার্নগুলি প্রশ্নের জন্য
    path('category/<int:category_id>/questions/', views.question_list, name='question_list'),
    path('category/<int:category_id>/questions/create/', views.create_question, name='create_question'),
    path('question/<int:question_id>/edit/', views.edit_question, name='edit_question'),

    # পরীক্ষা সেটিংসের জন্য URL প্যাটার্ন
    path('exam/<int:exam_id>/settings/create/', views.exam_settings_create, name='exam_settings_create'),
    path('exam/<int:exam_id>/settings/', views.exam_settings_detail, name='exam_settings_detail'),
    path('exam/<int:exam_id>/settings/update/', views.exam_settings_update, name='exam_settings_update'),
    path('exam/<int:exam_id>/settings/delete/', views.exam_settings_delete, name='exam_settings_delete'),
    path('exam-settings/', views.exam_settings_list, name='exam_settings_list'),

    # অতিরিক্ত URL প্যাটার্ন যোগ করুন
    # path('dashboard/', views.dashboard, name='dashboard'),
    path('start-exam/<int:exam_id>/', views.start_exam, name='start_exam'),
    path('submit-exam/<int:exam_id>/', views.submit_exam, name='submit_exam'),
    path('mock-exam/<int:category_id>/', views.start_mock_exam, name='start_mock_exam'),
    path('submit-mock-exam/', views.submit_mock_exam, name='submit_mock_exam'),
    # path('payment/<int:registration_id>/', views.payment, name='payment'),
    # path('notifications/', views.notifications, name='notifications'),
    path('performance-analysis/', views.performance_analysis, name='performance_analysis'),
    path('exam-confirmation/<int:registration_id>/', views.exam_confirmation, name='exam_confirmation'),
]

