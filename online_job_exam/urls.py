"""
URL configuration for online_job_exam project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from . import views
urlpatterns = [
    path('admin/', admin.site.urls),
    # path('', views.home, name='home'),
    # path('about/', views.about, name='about'),
    path('accounts/', include('accounts.urls')),
    # path('contact/', views.contact, name='contact'),
    path('exams/', include('exams.urls')),
    path('services/', include('services.urls')),
    path('liveExam/', include('liveExam.urls')),
    path('results/', include('results.urls')),
    path('dashboard/', include('dashboard.urls')),
    path('payments/', include('payments.urls')),
    path('notifications/', include('notifications.urls')),
    path('books/', include('books.urls')),
    path('blog/', include('blog.urls')),
    path('ckeditor5/', include('django_ckeditor_5.urls')),
    path('', include('core.urls')),
    path('tinymce/', include('tinymce.urls')),
    path('select2/', include('django_select2.urls')),
]+ static(settings.MEDIA_URL , document_root = settings.MEDIA_ROOT)
static(settings.STATIC_URL , document_root = settings.STATIC_ROOT)

