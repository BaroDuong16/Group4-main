from django.http import Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.db.utils import IntegrityError
from django.core.cache import cache

from module_group.models import ModuleGroup

from ..models import NewCourse, Quiz, Question, Answer_Option, Enrolled_Course, Sub_Course, Module, Sub_Module
from ..forms import Sub_Module_Form

from django.contrib.auth.decorators import login_required, user_passes_test


def sub_module_add(request, course_pk, sub_course_pk, module_pk):
    cache.set('last_sub_course_pk', sub_course_pk, timeout=60*5)

    course = get_object_or_404(NewCourse, pk=course_pk)
    sub_course = get_object_or_404(Sub_Course, pk=sub_course_pk)
    module = get_object_or_404(Module, pk=module_pk)

    num = len(module.sub_modules.all()) + 1

    if request.method == 'POST':
        form = Sub_Module_Form(request.POST)

        form.instance.module = module
        form.instance.order = num

        if form.is_valid():
            form = form.save()

            return redirect(reverse('course_Truong:sub_course_list', kwargs={'course_pk': course_pk}))
    else:
        form = Sub_Module_Form()

    context = {
        'form': form,
        'course_pk' : course_pk,
    }
    return render(request, 'sub_module_management/sub_module_form.html', context)


def sub_module_edit(request, course_pk, sub_course_pk, module_pk, sub_module_pk):
    cache.set('last_sub_course_pk', sub_course_pk, timeout=60*5)
    
    course = get_object_or_404(NewCourse, pk=course_pk)
    sub_course = get_object_or_404(Sub_Course, pk=sub_course_pk)
    module = get_object_or_404(Module, pk=module_pk)
    sub_module = get_object_or_404(Sub_Module, pk=sub_module_pk)

    if request.method == 'POST':
        form = Sub_Module_Form(request.POST, instance=sub_module)

        if form.is_valid():
            form = form.save()

            context = {
                'course_pk' : course_pk,
                'sub_course_pk' : sub_course_pk,
                'module_pk' : module_pk,
                'sub_module_pk' : sub_module_pk,
            }
            return redirect(reverse('course_Truong:sub_module_edit', kwargs=context))
    else:
        form = Sub_Module_Form(instance=sub_module)

    context = {
        'form': form,
        'course_pk' : course_pk,
    }
    return render(request, 'sub_module_management/sub_module_form.html', context)


def sub_module_delete(request, course_pk, sub_course_pk, module_pk, sub_module_pk):
    cache.set('last_sub_course_pk', sub_course_pk, timeout=60*5)

    course = get_object_or_404(NewCourse, pk=course_pk)
    sub_course = get_object_or_404(Sub_Course, pk=sub_course_pk)
    module = get_object_or_404(Module, pk=module_pk)
    sub_module = get_object_or_404(Sub_Module, pk=sub_module_pk)

    sub_course_num = sub_module.order
    sub_modules = module.sub_modules.all().order_by("order")

    if request.method == 'POST':
        sub_module.delete()
        for sub_module in sub_modules:
            if sub_module.order > sub_course_num:
                sub_module.order -= 1
                sub_module.save()
                
        cache.delete('last_sub_course_pk')
        return redirect(reverse('course_Truong:sub_course_list', kwargs={'course_pk': course_pk}))

    context = {
        'name': sub_module.title,
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