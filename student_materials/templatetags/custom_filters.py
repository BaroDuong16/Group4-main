import os
from django import template

register = template.Library()

@register.filter(name='basename')
def basename(value):
    """Returns the base name of a file."""
    return os.path.basename(value)
