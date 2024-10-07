from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.user_dashboard, name='user_dashboard'),
    path('performance-analysis/', views.performance_analysis, name='performance_analysis'),
    path('customize-dashboard/', views.customize_dashboard, name='customize_dashboard'),
    path('submit-feedback/', views.submit_feedback, name='submit_feedback'),
    path('change-profile-picture/', views.change_profile_picture, name='change_profile_picture'),
]
