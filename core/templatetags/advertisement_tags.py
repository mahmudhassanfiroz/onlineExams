from django import template
from core.models import Advertisement

register = template.Library()

@register.inclusion_tag('core/show_ad.html')
def show_advertisement(position):
    ad = Advertisement.objects.filter(is_active=True, position=position).first()
    return {'advertisement': ad}
