from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.user_dashboard, name='user_dashboard'),
    path('performance/', views.performance_metrics, name='performance_metrics'),
    path('customize/', views.customize_dashboard, name='customize_dashboard'),
    path('feedback/', views.submit_feedback, name='submit_feedback'),
]
