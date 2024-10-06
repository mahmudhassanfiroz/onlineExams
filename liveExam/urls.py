from django.urls import path
from . import views

app_name = 'liveExam'

urlpatterns = [
    path('', views.live_exam_list, name='live_exam_list'),
    path('free/', views.free_live_exams, name='free_live_exams'),
    path('my-exams/', views.user_live_exams, name='user_live_exams'),
    path('<slug:slug>/', views.live_exam_detail, name='live_exam_detail'),
    path('<slug:slug>/take/', views.take_live_exam, name='take_live_exam'),
    path('result/<int:exam_id>/', views.live_exam_result, name='live_exam_result'),
]
