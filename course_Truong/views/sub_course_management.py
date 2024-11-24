from django.http import Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.db.utils import IntegrityError
from django.core.cache import cache

from module_group.models import ModuleGroup

from ..models import NewCourse, Quiz, Question, Answer_Option, Enrolled_Course, Sub_Course
from ..forms import Sub_Course_Form

from django.contrib.auth.decorators import login_required, user_passes_test


def sub_course_list(request, course_pk):
    last_sub_course_pk = cache.get('last_sub_course_pk')
    cache.delete('last_sub_course_pk')
    module_groups = ModuleGroup.objects.all()

    course = get_object_or_404(NewCourse, pk=course_pk)

    sub_courses = course.sub_courses.all().order_by("order")

    context = {
        "module_groups" : module_groups,
        "last_sub_course_pk" : last_sub_course_pk,
        "course" : course,
        "sub_courses": {},
    }

    for sub_course in sub_courses:
        modules = sub_course.modules.all().order_by("order")
        quizzes = sub_course.quizzes.all().order_by("order")
        
        context['sub_courses'][sub_course] = {
            'modules': {},
            'quizzes': quizzes,
        }

        for module in modules:
            sub_modules = module.sub_modules.all().order_by("order")
            
            context['sub_courses'][sub_course]['modules'][module] = sub_modules

    return render(request, "sub_course_management/sub_course_list.html", context)


def sub_course_add(request, course_pk):
    course = get_object_or_404(NewCourse, pk=course_pk)
    num = len(course.sub_courses.all()) + 1

    if request.method == 'POST':
        form = Sub_Course_Form(request.POST)

        form.instance.course = course
        form.instance.order = num

        if form.is_valid():
            form = form.save()

            return redirect(reverse('course_Truong:sub_course_list', kwargs={'course_pk': course_pk}))
    else:
        form = Sub_Course_Form()

    context = {
        'form': form,
        'course_pk' : course_pk,
    }
    return render(request, 'sub_course_management/sub_course_form.html', context)


def sub_course_edit(request, course_pk, sub_course_pk):
    cache.set('last_sub_course_pk', sub_course_pk, timeout=60*5)
    course_content = get_object_or_404(Sub_Course, pk=sub_course_pk)
    if request.method == 'POST':
        form = Sub_Course_Form(request.POST, instance=course_content)

        if form.is_valid():
            form = form.save()

            return redirect(reverse('course_Truong:sub_course_list', kwargs={'course_pk': course_pk}))
    else:
        form = Sub_Course_Form(instance=course_content)

    context = {
        'form': form,
        'course_pk' : course_pk,
    }
    return render(request, 'sub_course_management/sub_course_form.html', context)


def sub_course_delete(request, course_pk, sub_course_pk):
    cache.set('last_sub_course_pk', sub_course_pk, timeout=60*5)
    
    course = get_object_or_404(NewCourse, pk=course_pk)

    sub_course = get_object_or_404(Sub_Course, pk=sub_course_pk)
    sub_course_num = sub_course.order
    contents = course.sub_courses.all().order_by("order")

    if request.method == 'POST':
        sub_course.delete()
        for content in contents:
            if content.order > sub_course_num:
                content.order -= 1
                content.save()
                
        cache.delete('last_sub_course_pk')
        return redirect(reverse('course_Truong:sub_course_list', kwargs={'course_pk': course_pk}))

    context = {
        'name': sub_course.title,
        'cancel_link': reverse('course_Truong:sub_course_list', kwargs={'course_pk': course_pk})
    }
    return render(request, 'confirm_delete.html', context)


def sub_course_move_up(request, course_pk, sub_course_pk):
    cache.set('last_sub_course_pk', sub_course_pk, timeout=60*5)
    course = get_object_or_404(NewCourse, pk=course_pk)

    course_content = get_object_or_404(Sub_Course, pk=sub_course_pk)
    sub_course_num = course_content.order

    if sub_course_num != 1:
        content = course.sub_courses.filter(order= (sub_course_num - 1))[0]
        content.order = 0
        content.save()

        course_content.order = (sub_course_num - 1)
        course_content.save()

        content = course.sub_courses.filter(order= 0)[0]
        content.order = sub_course_num
        content.save()
    return redirect(reverse('course_Truong:sub_course_list', kwargs={'course_pk': course_pk}))


def sub_course_move_down(request, course_pk, sub_course_pk):
    cache.set('last_sub_course_pk', sub_course_pk, timeout=60*5)
    course = get_object_or_404(NewCourse, pk=course_pk)

    course_content = get_object_or_404(Sub_Course, pk=sub_course_pk)
    sub_course_num = course_content.order
    len_content = len(course.sub_courses.all())

    if sub_course_num != len_content:
        content = course.sub_courses.filter(order= (sub_course_num + 1))[0]
        content.order = 0
        content.save()

        course_content.order = (sub_course_num + 1)
        course_content.save()

        content = course.sub_courses.filter(order= 0)[0]
        content.order = sub_course_num
        content.save()
    return redirect(reverse('course_Truong:sub_course_list', kwargs={'course_pk': course_pk}))
