# In student_materials/templatetags/material_tags.py

from django import template

register = template.Library()

@register.filter(name='is_folder')
def is_folder(link):
    """Check if the google drive link points to a folder"""
    return "folders" in link
