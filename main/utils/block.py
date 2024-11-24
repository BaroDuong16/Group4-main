from functools import wraps
from django.urls import reverse
from django.shortcuts import render, redirect, get_object_or_404
from typing import Callable, Any, List

def custom_user_passes_test(
        test_func: Callable[[Any], bool],
        url_name_space: str | None = None,
        reverse_kwarg_keys: List[str] = [],
        *decorator_args,
        **decorator_kwargs
    ):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            profile = request.user.profile  # Access the user's profile
            if test_func(profile, *args, *decorator_args, **kwargs, **decorator_kwargs):
                return view_func(request, *args, **kwargs)
            else:
                return redirect(reverse(url_name_space, kwargs={key: kwargs[key] for key in reverse_kwarg_keys}))
        return _wrapped_view
    return decorator


def block_student(profile):
    return profile.role.role_name != 'Student'


def block_instructor(profile):
    return profile.role.role_name != 'Teacher' #Instructor


# def block_unenrolled_student(profile, course_pk, *args, **kwargs):
#     return len(profile.enrolled_courses.filter(course=course_pk)) == 1

def block_unenrolled_student(profile, course_pk, *args, **kwargs):
    if profile.student:
        return profile.student.enrolled_courses.filter(pk=course_pk).count() == 0
    return True  # If the profile has no student, block access

def block_by_role_name(profile, roles_name: list | str, *args, **kwargs):
    if isinstance(roles_name, str):
        roles_name = [roles_name]
    
    return profile.role.role_name not in roles_name


# def block_by_role_name(profile, roles_name: list|str, *args, **kwargs):
#     for role_name in roles_name:
#         if profile.role.role_name == role_name:
#             return False
#     return True





