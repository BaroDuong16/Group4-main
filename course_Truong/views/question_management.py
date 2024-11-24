from django.http import Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse

from module_group.models import ModuleGroup

from ..forms import Course_Form, Quiz_Form, Question_Form, Answer_Option_Form
from ..models import NewCourse, Quiz, Question, Answer_Option, Sub_Course

from django.contrib.auth.decorators import login_required, user_passes_test
from main.utils.block import block_student


@login_required
@user_passes_test(block_student)
def question_add(request, course_pk, sub_course_pk, quiz_pk):
    course = get_object_or_404(NewCourse, pk=course_pk)
    sub_course = get_object_or_404(Sub_Course, pk=sub_course_pk)
    quiz = get_object_or_404(Quiz, pk=quiz_pk)

    if request.method == 'POST':
        form = Question_Form(request.POST)

        form.instance.quiz = quiz
        
        if form.is_valid():
            form = form.save()
            Quiz.objects.get(pk=quiz_pk).save()

            return redirect(reverse('course_Truong:quiz_detail', kwargs={'course_pk': course_pk, 'sub_course_pk': sub_course_pk, 'quiz_pk': quiz_pk}))
    else:
        form = Question_Form()

    context = {
        'form': form,
        'course_pk' : course_pk,
        'sub_course_pk' : sub_course_pk,
        'quiz_pk' : quiz_pk,
    }
    return render(request, 'question_management/question_form.html', context)


@login_required
@user_passes_test(block_student)
def question_delete(request, course_pk, sub_course_pk, quiz_pk, question_pk):
    course = get_object_or_404(NewCourse, pk=course_pk)
    sub_course = get_object_or_404(Sub_Course, pk=sub_course_pk)
    quiz = get_object_or_404(Quiz, pk=quiz_pk)
    question = get_object_or_404(Question, pk=question_pk)

    if request.method == 'POST':
        question.delete()
        Quiz.objects.get(pk=quiz_pk).save()

        return redirect(reverse('course_Truong:quiz_detail', kwargs={'course_pk': course_pk, 'sub_course_pk': sub_course_pk, 'quiz_pk': quiz_pk}))
    
    context = {
        'name': question.question_text,
        'cancel_link': reverse('course_Truong:quiz_detail', kwargs={'course_pk': course_pk, 'sub_course_pk': sub_course_pk, 'quiz_pk': quiz_pk})
    }
    return render(request, 'confirm_delete.html', context)


@login_required
@user_passes_test(block_student)
def question_edit(request, course_pk, sub_course_pk, quiz_pk, question_pk):
    course = get_object_or_404(NewCourse, pk=course_pk)
    sub_course = get_object_or_404(Sub_Course, pk=sub_course_pk)
    quiz = get_object_or_404(Quiz, pk=quiz_pk)
    question = get_object_or_404(Question, pk=question_pk)

    if request.method == 'POST':
        form = Question_Form(request.POST, instance=question)

        if form.is_valid():
            form = form.save()
            Quiz.objects.get(pk=quiz_pk).save()

            return redirect(reverse('course_Truong:quiz_detail', kwargs={'course_pk': course_pk, 'sub_course_pk': sub_course_pk, 'quiz_pk': quiz_pk}))
    else:
        form = Question_Form(instance=question)

    context = {
        'form': form,
        'course_pk' : course_pk,
        'sub_course_pk' : sub_course_pk,
        'quiz_pk' : quiz_pk,
    }
    return render(request, 'question_management/question_form.html', context)