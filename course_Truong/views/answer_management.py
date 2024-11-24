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
def answer_add(request, course_pk, sub_course_pk, quiz_pk, question_pk):
    course = get_object_or_404(NewCourse, pk=course_pk)
    sub_course = get_object_or_404(Sub_Course, pk=sub_course_pk)
    quiz = get_object_or_404(Quiz, pk=quiz_pk)
    question = get_object_or_404(Question, pk=question_pk)

    if request.method == 'POST':
        form = Answer_Option_Form(request.POST)

        form.instance.question = question
        
        if form.is_valid():
            form = form.save()
            Quiz.objects.get(pk=quiz_pk).save()

            return redirect(reverse('course_Truong:quiz_detail', kwargs={'course_pk': course_pk, 'sub_course_pk': sub_course_pk, 'quiz_pk': quiz_pk}))
    else:
        form = Answer_Option_Form()

    context = {
        'form': form,
        'course_pk' : course_pk,
        'sub_course_pk' : sub_course_pk,
        'quiz_pk' : quiz_pk,
    }
    return render(request, 'answer_management/answer_form.html', context)


@login_required
@user_passes_test(block_student)
def answer_edit(request, course_pk, sub_course_pk, quiz_pk, question_pk, answer_pk):
    course = get_object_or_404(NewCourse, pk=course_pk)
    sub_course = get_object_or_404(Sub_Course, pk=sub_course_pk)
    quiz = get_object_or_404(Quiz, pk=quiz_pk)
    question = get_object_or_404(Question, pk=question_pk)
    answer = get_object_or_404(Answer_Option, pk=answer_pk)

    if request.method == 'POST':
        form = Answer_Option_Form(request.POST, instance=answer)

        if form.is_valid():
            form = form.save()
            Quiz.objects.get(pk=quiz_pk).save()

            return redirect(reverse('course_Truong:quiz_detail', kwargs={'course_pk': course_pk, 'sub_course_pk': sub_course_pk, 'quiz_pk': quiz_pk}))
    else:
        form = Answer_Option_Form(instance=answer)

    context = {
        'form': form,
        'course_pk' : course_pk,
        'sub_course_pk' : sub_course_pk,
        'quiz_pk' : quiz_pk,
    }
    return render(request, 'answer_management/answer_form.html', context)


@login_required
@user_passes_test(block_student)
def answer_delete(request, course_pk, sub_course_pk, quiz_pk, question_pk, answer_pk):
    course = get_object_or_404(NewCourse, pk=course_pk)
    sub_course = get_object_or_404(Sub_Course, pk=sub_course_pk)
    quiz = get_object_or_404(Quiz, pk=quiz_pk)
    question = get_object_or_404(Question, pk=question_pk)
    answer = get_object_or_404(Answer_Option, pk=answer_pk)

    if request.method == 'POST':
        answer.delete()
        Quiz.objects.get(pk=quiz_pk).save()

        return redirect(reverse('course_Truong:quiz_detail', kwargs={'course_pk': course_pk, 'sub_course_pk': sub_course_pk, 'quiz_pk': quiz_pk}))
    
    context = {
        'name': answer.option_text,
        'cancel_link': reverse('course_Truong:quiz_detail', kwargs={'course_pk': course_pk, 'sub_course_pk': sub_course_pk, 'quiz_pk': quiz_pk})
    }
    return render(request, 'confirm_delete.html', context)