from django.http import Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.core.cache import cache

from module_group.models import ModuleGroup

from ..forms import Image_Form
from ..models import NewCourse, Image

from django.contrib.auth.decorators import login_required, user_passes_test
from main.utils.block import block_student


@login_required
@user_passes_test(block_student)
def image_list(request, course_pk):
    course = get_object_or_404(NewCourse, pk=course_pk)
    images = course.images.all()
    print(images)
    module_groups = ModuleGroup.objects.all()

    context = {
        'module_groups' : module_groups,
        "course" : course,
        "images" : images,
    }
    return render(request, 'image_management/image_list.html', context)


@login_required
@user_passes_test(block_student)
def image_add(request, course_pk):
    course = get_object_or_404(NewCourse, pk= course_pk)

    if request.method == 'POST':
        for img in request.FILES.getlist('images'):
            Image.objects.create(image=img, course=course)
        return redirect(reverse('course_Truong:image_list', kwargs={'course_pk': course_pk}))
    # else:
    #     pass

    context = {
        'course_pk' : course_pk
    }
    return render(request, 'image_management/image_form.html', context)


@login_required
@user_passes_test(block_student)
def image_delete(request, course_pk, image_pk):
    course = get_object_or_404(NewCourse, pk=course_pk)
    image = get_object_or_404(Image, pk=image_pk)

    if request.method == 'POST':
        image.delete()
        return redirect(reverse('course_Truong:image_list', kwargs={'course_pk': course_pk}))
    
    context = {
        'name': image.image,
        'cancel_link': reverse('course_Truong:image_list', kwargs={'course_pk': course_pk})
    }
    return render(request, 'confirm_delete.html', context)