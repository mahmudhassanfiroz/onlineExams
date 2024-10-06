from django import template
from core.models import Advertisement

register = template.Library()

@register.inclusion_tag('core/advertisements.html')
def show_advertisements(position):
    advertisements = Advertisement.objects.filter(is_active=True, position=position)
    return {'advertisements': advertisements}

