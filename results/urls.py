
from django.urls import path
from . import views

app_name = 'results'

urlpatterns = [
    path('overview/', views.results_overview, name='overview'),
    path('result/<int:result_id>/', views.individual_result, name='individual_result'),
    path('analysis/<int:result_id>/', views.result_analysis, name='result_analysis'),
    path('pdf/<int:result_id>/', views.generate_pdf, name='generate_pdf'),
    path('leaderboard/<int:exam_id>/', views.leaderboard, name='leaderboard'),
    path('comparison/', views.result_comparison, name='result_comparison'),
    path('feedback/<int:result_id>/', views.submit_feedback, name='submit_feedback'),
]
