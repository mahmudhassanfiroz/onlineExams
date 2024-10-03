from django import template
from services.models import ServiceCategory, Service

register = template.Library()

@register.simple_tag
def get_service_categories():
    return ServiceCategory.objects.all()

@register.simple_tag
def get_services_by_category(category):
    return Service.objects.filter(category=category, slug__isnull=False).select_related('category')

