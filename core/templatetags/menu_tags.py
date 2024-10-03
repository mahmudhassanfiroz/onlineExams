from django import template
from core.models import MenuItem

register = template.Library()

@register.simple_tag
def get_menu_items():
    return MenuItem.objects.filter(parent=None).order_by('order')
