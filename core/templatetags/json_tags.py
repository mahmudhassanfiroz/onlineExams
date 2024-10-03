from django import template
from django.utils.safestring import mark_safe
import json

register = template.Library()

@register.filter(is_safe=True)
def json_script(value):
    if value is None:
        return mark_safe('null')
    return mark_safe(json.dumps(value))

