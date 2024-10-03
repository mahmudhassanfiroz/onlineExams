from django import template

register = template.Library()

@register.filter(name='type_of')
def type_of(value):
    return type(value).__name__

