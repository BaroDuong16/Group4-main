from django.http import Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.db.utils import IntegrityError
from django.core.cache import cache

from ..models import NewCourse, Quiz, Question, Answer_Option, Enrolled_Course, Sub_Course, Module
from ..forms import Module_Form

from django.contrib.auth.decorators import login_required, user_passes_test


def module_add(request, course_pk, sub_course_pk):
    cache.set('last_sub_course_pk', sub_course_pk, timeout=60*5)

    sub_course = get_object_or_404(Sub_Course, pk= sub_course_pk)
    num_module = len(sub_course.modules.all())

    if request.method == 'POST':
        form = Module_Form(request.POST)

        form.instance.sub_course = sub_course
        form.instance.created_by = request.user
        form.instance.order = num_module + 1
        
        if form.is_valid():
            form = form.save()
            return redirect(reverse('course_Truong:sub_course_list', kwargs={'course_pk': course_pk}))
    else:
        form = Module_Form()

    context = {
        'form': form,
        'course_pk' : course_pk
    }
    return render(request, 'module_management/module_form.html', context)


def module_edit(request, course_pk, sub_course_pk, module_pk):
    cache.set('last_sub_course_pk', sub_course_pk, timeout=60*5)

    course = get_object_or_404(NewCourse, pk= course_pk)
    sub_course = get_object_or_404(Sub_Course, pk= sub_course_pk)
    module = get_object_or_404(Module, pk= module_pk)

    if request.method == 'POST':
        form = Module_Form(request.POST, instance=module)

        if form.is_valid():
            form = form.save()
            return redirect(reverse('course_Truong:sub_course_list', kwargs={'course_pk': course_pk}))
    else:
        form = Module_Form(instance=module)

    context = {
        'form': form,
        'course_pk' : course_pk
    }
    return render(request, 'module_management/module_form.html', context)


def module_delete(request, course_pk, sub_course_pk, module_pk):
    cache.set('last_sub_course_pk', sub_course_pk, timeout=60*5)

    course = get_object_or_404(NewCourse, pk=course_pk)
    sub_course = get_object_or_404(Sub_Course, pk=sub_course_pk)
    module = get_object_or_404(Module, pk=module_pk)

    num = module.order
    modules = sub_course.modules.all().order_by("order")

    if request.method == 'POST':
        module.delete()
        for module in modules:
            if module.order > num:
                module.order -= 1
                module.save()
                
        cache.delete('last_sub_course_pk')
        return redirect(reverse('course_Truong:sub_course_list', kwargs={'course_pk': course_pk}))

    context = {
        'name': module.title,
        'cancel_link': reverse('course_Truong:sub_course_list', kwargs={'course_pk': course_pk})
    }
    return render(request, 'confirm_delete.html', context)


def module_move_up(request, course_pk, sub_course_pk, module_pk):
    cache.set('last_sub_course_pk', sub_course_pk, timeout=60*5)
    sub_course = get_object_or_404(Sub_Course, pk=sub_course_pk)

    module = get_object_or_404(Module, pk=module_pk)
    module_num = module.order
    if module_num != 1:
        module_temp = sub_course.modules.filter(order= (module_num - 1))[0]
        module_temp.order = 0
        module_temp.save()

        module.order = (module_num - 1)
        module.save()

        module_temp = sub_course.modules.filter(order= 0)[0]
        module_temp.order = module_num
        module_temp.save()
    return redirect(reverse('course_Truong:sub_course_list', kwargs={'course_pk': course_pk}))


def module_move_down(request, course_pk, sub_course_pk, module_pk):
    cache.set('last_sub_course_pk', sub_course_pk, timeout=60*5)
    sub_course = get_object_or_404(Sub_Course, pk=sub_course_pk)

    module = get_object_or_404(Module, pk=module_pk)
    module_num = module.order
    num_module = len(sub_course.modules.all())

    if module_num != num_module:
        module_temp = sub_course.modules.filter(order= (module_num + 1))[0]
        module_temp.order = 0
        module_temp.save()

        module.order = (module_num + 1)
        module.save()

        module_temp = sub_course.modules.filter(order= 0)[0]
        module_temp.order = module_num
        module_temp.save()
    return redirect(reverse('course_Truong:sub_course_list', kwargs={'course_pk': course_pk}))