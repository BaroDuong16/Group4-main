from django import template

register = template.Library()

@register.filter
def split(value, delimiter=','):
    """Splits a string by the given delimiter."""
    return value.split(delimiter)

@register.filter(name='add_class')
def add_class(field, css_class):
    """
    Adds a CSS class to form fields in templates.
    """
    return field.as_widget(attrs={"class": css_class})