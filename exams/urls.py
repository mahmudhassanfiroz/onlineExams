from django.urls import path
from . import views

app_name = 'exams'

urlpatterns = [
    path('', views.exam_list, name='exam_list'),
    path('free/', views.free_exams, name='free_exams'),
    path('my-exams/', views.user_exams, name='user_exams'),
    path('<slug:slug>/', views.exam_detail, name='exam_detail'),
    path('<slug:slug>/take/', views.take_exam, name='take_exam'),
    path('result/<int:exam_id>/', views.exam_result, name='exam_result'),
]
