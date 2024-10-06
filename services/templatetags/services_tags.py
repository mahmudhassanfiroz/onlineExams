from django import template
from services.models import ExamCategory, Package, UserPackage
from django.db.models import Prefetch
from django.utils import timezone

register = template.Library()

@register.simple_tag
def get_exam_categories():
    return ExamCategory.objects.all()

@register.simple_tag
def get_packages_by_type(package_type):
    return Package.objects.filter(package_type=package_type).prefetch_related('exam_categories')

@register.simple_tag
def get_featured_packages():
    return Package.objects.filter(is_featured=True).prefetch_related('exam_categories')

@register.simple_tag(takes_context=True)
def get_user_packages(context):
    user = context['user']
    if user.is_authenticated:
        return UserPackage.objects.filter(
            user=user,
            is_active=True,
            expiry_date__gt=timezone.now()
        ).select_related('package').prefetch_related('package__exam_categories')
    return []

@register.simple_tag
def get_coaching_packages():
    return Package.objects.filter(package_type='COACHING').prefetch_related('exam_categories')

@register.simple_tag
def get_student_packages():
    return Package.objects.filter(package_type='STUDENT').prefetch_related('exam_categories')

