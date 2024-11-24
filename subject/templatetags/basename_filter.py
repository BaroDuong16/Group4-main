import os
from django import template

register = template.Library()

@register.filter
def basename(value):
    """Returns the base name of the file."""
    return os.path.basename(value)
