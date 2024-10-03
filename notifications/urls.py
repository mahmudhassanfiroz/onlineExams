from django.urls import path
from . import views

app_name = 'notifications'

urlpatterns = [
    path('list/', views.notification_list, name='notification_list'),
    path('mark-as-read/<int:notification_id>/', views.mark_as_read, name='mark_as_read'),
    path('schedule-exam/<int:exam_id>/', views.schedule_exam, name='schedule_exam'),
    path('publish-result/<int:exam_id>/', views.publish_result, name='publish_result'),
]
