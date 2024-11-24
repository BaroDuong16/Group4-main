"""
    Creating, modifying, and deleting courses or course parts
"""
import re
import os
import shutil
import random
import json
from PIL import Image
import pandas as pd

from django.http import Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse

from module_group.models import ModuleGroup

from ..forms import Course_Form, Quiz_Form, Question_Form, Answer_Option_Form
from ..models import NewCourse, Sub_Course, Module, Sub_Module, Quiz, Question, Answer_Option

from django.contrib.auth.decorators import login_required, user_passes_test
from main.utils.block import block_student, block_by_role_name, custom_user_passes_test

from django.contrib import messages

def compress_image(image_path):
    with Image.open(image_path) as img:
        img = img.resize((800, 450), Image.Resampling.BILINEAR)
        img.save(image_path)


@login_required
@custom_user_passes_test(block_by_role_name, "main:home", roles_name='Student')
def course_list(request):
    context = {}

    module_groups = ModuleGroup.objects.all()
    courses = NewCourse.objects.all()

    context['module_groups'] = module_groups
    context['courses'] = courses
    return render(request, 'course_management/course_list.html', context)


@login_required
@custom_user_passes_test(block_by_role_name, "main:home", roles_name='Student')
def course_delete(request, course_pk):
    course = get_object_or_404(NewCourse, pk=course_pk)
    if request.method == 'POST':
        course.delete()
        return redirect('course_Truong:course_list')
    
    context = {
        'name': course.course_name,
        'cancel_link': reverse('course_Truong:course_list')
    }
    return render(request, 'confirm_delete.html', context)


@login_required
@custom_user_passes_test(block_by_role_name, "main:home", roles_name='Student')
def course_add(request):
    if request.method == 'POST':
        form = Course_Form(request.POST, request.FILES)
        if form.is_valid():
            form = form.save()

            compress_image(form.image.path)
            return redirect('course_Truong:course_list')
    else:
        form = Course_Form(request.POST, request.FILES)

    return render(request, 'course_management/basic_info_form.html', {'form': form})


@login_required
@custom_user_passes_test(block_by_role_name, "main:home", roles_name='Student')
def course_edit(request, course_pk):
    course = get_object_or_404(NewCourse, pk=course_pk)
    old_img_path = course.image.path

    if request.method == 'POST':
        form = Course_Form(request.POST, request.FILES, instance=course)
        if form.is_valid():

            course_info = form.save()
            compress_image(course_info.image.path)
            
            new_img_path = course.image.path

            if old_img_path != new_img_path:
                try:
                    os.remove(old_img_path)
                except FileNotFoundError:
                    pass

            return redirect(reverse('course_Truong:course_view', kwargs={'course_pk': course_pk}))
    else:
        form = Course_Form(instance=course)
    return render(request, 'course_management/basic_info_form.html', {'form': form})


@login_required
@custom_user_passes_test(block_by_role_name, "main:home", roles_name='Student')
def course_view(request, course_pk):
    course = get_object_or_404(NewCourse, pk=course_pk)
    
    module_groups = ModuleGroup.objects.all()

    context = {
        'module_groups' : module_groups,
        "course" : course,
    }

    return render(request, 'course_management/course_view.html', context)


@login_required
@custom_user_passes_test(block_by_role_name, "main:home", roles_name='Student')
def upload_existed_course(request):
    def is_valid_url(url: str) -> bool:
        if not isinstance(url, str):
            return False
        
        url_pattern = re.compile(
            r'^(https?|ftp)://[^\s/$.?#].[^\s]*$'
        )

        return re.match(url_pattern, url) is not None

    if request.method == "POST":
        json_data = request.FILES['json_data']

        json_data = json.load(json_data)
        print(json_data)

        for course_name, course_items in json_data.items():
            image_file_path = f"images/default_image_{random.randint(0,10000000)}.jpg"
            course = Course.objects.create(
                course_name= course_name,
                image= image_file_path,
                description= course_items['description']
            )
            for sub_course_title, sub_course_items in course_items['sub_courses'].items():
                order = len(course.sub_courses.all()) + 1
                sub_course, _ = Sub_Course.objects.get_or_create(
                    title= sub_course_title,
                    course= course,
                    defaults= {
                        "order": order
                    }
                )
                for module_title, module_items in sub_course_items['modules'].items():
                    order = len(sub_course.modules.all()) + 1
                    module, _ = Module.objects.get_or_create(
                        title= module_title,
                        sub_course= sub_course,
                        defaults= {
                            "order": order,
                            "created_by": request.user
                        }
                    )
                    for sub_module_title, sub_module_items in module_items.items():          
                        order = len(module.sub_modules.all()) + 1
                        sub_module, _ = Sub_Module.objects.get_or_create(
                            title= sub_module_title,
                            module= module,
                            defaults={
                                "order": order,
                                "video_url": sub_module_items['video_url'],
                                "html_content": sub_module_items['html_content'],
                            }
                        )
                order = 0
                for quiz_title, quiz_items in sub_course_items['quizzes'].items():
                    order += 1
                    quiz = Quiz.objects.create(
                        quiz_title = quiz_title,
                        quiz_description = quiz_items['description'],
                        total_mark = quiz_items['total_mark'],
                        mark_to_pass = quiz_items['mark_to_pass'],
                        order = order,
                        created_by = request.user,
                        sub_course = sub_course
                    )
                    for question_text, question_items in quiz_items['questions'].items():
                        question = Question.objects.create(
                            question_text = question_text,
                            question_type = question_items['type'],
                            points = question_items['point'],
                            quiz = quiz
                        )
                        for option_text, is_correct in question_items['answers'].items():
                            answer = Answer_Option.objects.create(
                                option_text = option_text,
                                is_correct = True if is_correct == 'true' else False,
                                question = question,
                            )
        return redirect('course_Truong:course_list')
    
    return render(request, 'upload_existed_course_form.html')