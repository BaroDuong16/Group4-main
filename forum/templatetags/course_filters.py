# forum/templatetags/course_filters.py
from django import template
from course.models import Course

register = template.Library()

@register.filter
def get_selected_course_name(courses, selected_course_id):
    selected_course = courses.filter(id=selected_course_id).first()
    return selected_course.course_name if selected_course else ''
