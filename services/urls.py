from django.urls import path
from . import views

app_name = 'services'

urlpatterns = [
    path('packages/<slug:slug>/', views.package_detail, name='package_detail'),
    path('packages/<slug:slug>/purchase/', views.purchase_package, name='purchase_package'),
    path('my-packages/', views.user_packages, name='user_packages'),
    path('search/', views.search_packages, name='search_packages'),
]
