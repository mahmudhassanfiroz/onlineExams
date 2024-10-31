
# exams/templatetags/custom_filters.py
from django import template

register = template.Library()

@register.filter(name='split')
def split(value, separator=' '):
    """Splits a string by the given separator."""
    return value.split(separator)
