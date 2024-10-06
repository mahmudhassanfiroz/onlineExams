from django.urls import path
from . import views

app_name = 'notifications'

urlpatterns = [
    path('', views.notification_list, name='notification_list'),
    path('<int:notification_id>/', views.notification_detail, name='notification_detail'),
    path('<int:notification_id>/mark-as-read/', views.mark_notification_as_read, name='mark_as_read'),
    path('preferences/', views.update_notification_preferences, name='update_notification_preferences'),
]
