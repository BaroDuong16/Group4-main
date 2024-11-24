"""
    For student activity: enroll, learn, quiz, ...
"""
from django.http import Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.db.utils import IntegrityError

from module_group.models import ModuleGroup

from ..models import NewCourse, Quiz, Question, Answer_Option, Enrolled_Course, Module, Sub_Course, Sub_Module

from django.contrib.auth.decorators import login_required
from main.utils.block import custom_user_passes_test, block_unenrolled_student

from .utils import query_all_sub_courses

def short_link_course(request, course_pk):
    course = get_object_or_404(NewCourse, pk=course_pk)
    course_name = course.url()
    return redirect(reverse('course_Truong:course_preview', kwargs={'course_pk': course_pk, 'course_name': course_name}))


def course_preview(request, course_pk, course_name):
    course = get_object_or_404(NewCourse, pk=course_pk)
    if course_name != course.url():
        raise Http404("Incorrect course name!")

    created_by = set()

    if request.user.is_authenticated:
        enrolled_users = course.enrolled_users.filter(user= request.user)
        is_enrolled = True if enrolled_users else False
    else:
        is_enrolled = False

    context = {
        "course" : course,
        "created_by" : created_by,
        "is_enrolled" : is_enrolled,
        "sub_courses" : {}
    }

    sub_courses = course.sub_courses.all()
    for sub_course in sub_courses:
        modules = sub_course.modules.all().order_by("order")
        quizzes = sub_course.quizzes.all().order_by("order")
        
        context['sub_courses'][sub_course] = {
            'modules': {},
            'quizzes': quizzes,
        }

        for module in modules:
            sub_modules = module.sub_modules.all().order_by("order")
            created_by.add(module.created_by.full_name)

            context['sub_courses'][sub_course]['modules'][module] = sub_modules

    return render(request, 'course_operations/course_preview.html', context)
    

@login_required
def course_enroll(request, course_pk):
    course = get_object_or_404(NewCourse, pk=course_pk)
    
    try:
        enrolling = Enrolled_course(course= course, user=request.user)
        enrolling.save()
    except IntegrityError:
        pass

    return redirect(reverse('course_Truong:short_link_course', kwargs={'course_pk': course_pk}))


@login_required
@custom_user_passes_test(block_unenrolled_student, "course_Truong:short_link_course", ["course_pk"])
def short_link_learning_view(request, course_pk, sub_module_pk):
    course = get_object_or_404(NewCourse, pk=course_pk)
    course_name = course.url()
    
    sub_module = get_object_or_404(Sub_Module, pk=sub_module_pk)

    return redirect(reverse('course_Truong:learning_view', kwargs={'course_pk': course_pk, 'course_name': course_name, 'sub_module_pk': sub_module_pk}))


@login_required
@custom_user_passes_test(block_unenrolled_student, "course_Truong:short_link_course", ["course_pk"])
def learning_view(request, course_pk, course_name, sub_module_pk):
    course = get_object_or_404(NewCourse, pk=course_pk)
    if course_name != course.url():
        raise Http404("Incorrect course name!")
    
    sub_module = get_object_or_404(Sub_Module, pk=sub_module_pk)

    context = {
        "course" : course,
        "sub_module" : sub_module,
        "sub_courses" : {}
    }

    query_all_sub_courses(course, context)

    return render(request, 'course_operations/main_view.html', context)