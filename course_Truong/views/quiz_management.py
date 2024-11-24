from django.http import Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.core.cache import cache

from module_group.models import ModuleGroup

from ..forms import Course_Form, Quiz_Form, Question_Form, Answer_Option_Form
from ..models import NewCourse, Quiz, Question, Answer_Option, Sub_Course

from django.contrib.auth.decorators import login_required, user_passes_test
from main.utils.block import block_student


@login_required
@user_passes_test(block_student)
def quiz_list(request, course_pk):
    course = get_object_or_404(NewCourse, pk=course_pk)
    module_groups = ModuleGroup.objects.all()
    quizzes = Quiz.objects.filter(course=course)
    all_questions = {}

    for quiz in quizzes:
        questions = Question.objects.filter(quiz=quiz)
        temp = {}
        for question in questions:
            answers = Answer_Option.objects.filter(question=question)
            temp[question] = answers

        all_questions[quiz.pk] = temp

    context = {
        'module_groups' : module_groups,
        "course" : course,
        "quizzes" : quizzes,
        "all_questions" : all_questions,
    }
    return render(request, 'quiz_management/quiz_list.html', context)


@login_required
@user_passes_test(block_student)
def quiz_delete(request, course_pk, sub_course_pk, quiz_pk):
    course = get_object_or_404(NewCourse, pk=course_pk)
    sub_course = get_object_or_404(Sub_Course, pk=sub_course_pk)
    quiz = get_object_or_404(Quiz, pk=quiz_pk)

    if request.method == 'POST':
        order = quiz.order
        quiz.delete()
        
        quizzes = sub_course.quizzes.all().order_by("order")
        for quiz in quizzes:
            if quiz.order > order:
                quiz.order -= 1
                quiz.save()

        return redirect(reverse('course_Truong:sub_course_list', kwargs={'course_pk': course_pk}))
    
    context = {
        'name': quiz.quiz_title,
        'cancel_link': reverse('course_Truong:quiz_detail', kwargs={'course_pk': course_pk, 'sub_course_pk' : sub_course_pk,'quiz_pk': quiz_pk})
    }
    return render(request, 'confirm_delete.html', context)


@login_required
@user_passes_test(block_student)
def quiz_add(request, course_pk, sub_course_pk):
    cache.set('last_sub_course_pk', sub_course_pk, timeout=60*5)

    sub_course = get_object_or_404(Sub_Course, pk= sub_course_pk)
    num_quiz = len(sub_course.quizzes.all())

    if request.method == 'POST':
        form = Quiz_Form(request.POST)

        form.instance.sub_course = sub_course
        form.instance.created_by = request.user
        form.instance.order = num_quiz + 1
        
        if form.is_valid():
            form = form.save()
            return redirect(reverse('course_Truong:sub_course_list', kwargs={'course_pk': course_pk}))
    else:
        form = Quiz_Form()

    context = {
        'form': form,
        'course_pk' : course_pk
    }
    return render(request, 'quiz_management/quiz_form.html', context)


@login_required
@user_passes_test(block_student)
def quiz_edit(request, course_pk, sub_course_pk, quiz_pk):
    course = get_object_or_404(NewCourse, pk=course_pk)
    content = get_object_or_404(Sub_Course, pk=sub_course_pk)
    quiz = get_object_or_404(Quiz, pk=quiz_pk)

    if request.method == 'POST':
        form = Quiz_Form(request.POST, instance=quiz)

        if form.is_valid():
            form = form.save()
            return redirect(reverse('course_Truong:quiz_detail', kwargs={'course_pk': course_pk, 'sub_course_pk' : sub_course_pk, 'quiz_pk': quiz_pk}))
    else:
        form = Quiz_Form(instance=quiz)

    context = {
        'form': form,
        'course_pk' : course_pk,
        'sub_course_pk' : sub_course_pk,
        'quiz_pk' : quiz_pk
    }
    return render(request, 'quiz_management/quiz_form.html', context)


@login_required
@user_passes_test(block_student)
def quiz_detail(request, course_pk, sub_course_pk, quiz_pk):
    cache.set('last_sub_course_pk', sub_course_pk, timeout=60*5)
    
    module_groups = ModuleGroup.objects.all()
    course = get_object_or_404(NewCourse, pk=course_pk)
    sub_course = get_object_or_404(Sub_Course, pk=sub_course_pk)
    quiz = get_object_or_404(Quiz, pk=quiz_pk)

    questions = Question.objects.filter(quiz=quiz)
    questions_and_answers = {}

    for question in questions:
        answers = Answer_Option.objects.filter(question=question)
        questions_and_answers[question] = answers

        # 'module_groups' : module_groups,
    context = {
        "course" : course,
        "sub_course" : sub_course,
        "quiz" : quiz,
        "questions_and_answers" : questions_and_answers,
    }
    return render(request, 'quiz_management/quiz_detail.html', context)


def quiz_move_up(request, course_pk, sub_course_pk, quiz_pk):
    cache.set('last_sub_course_pk', sub_course_pk, timeout=60*5)
    sub_course = get_object_or_404(Sub_Course, pk=sub_course_pk)

    quiz = get_object_or_404(Quiz, pk=quiz_pk)
    quiz_num = quiz.order
    if quiz_num != 1:
        quiz_temp = sub_course.quizzes.filter(order= (quiz_num - 1))[0]
        quiz_temp.order = 0
        quiz_temp.save()

        quiz.order = (quiz_num - 1)
        quiz.save()

        quiz_temp = sub_course.quizzes.filter(order= 0)[0]
        quiz_temp.order = quiz_num
        quiz_temp.save()
    return redirect(reverse('course_Truong:sub_course_list', kwargs={'course_pk': course_pk}))


def quiz_move_down(request, course_pk, sub_course_pk, quiz_pk):
    cache.set('last_sub_course_pk', sub_course_pk, timeout=60*5)
    sub_course = get_object_or_404(Sub_Course, pk=sub_course_pk)

    quiz = get_object_or_404(Quiz, pk=quiz_pk)
    quiz_num = quiz.order
    num_quiz = len(sub_course.quizzes.all())

    if quiz_num != num_quiz:
        quiz_temp = sub_course.quizzes.filter(order= (quiz_num + 1))[0]
        quiz_temp.order = 0
        quiz_temp.save()

        quiz.order = (quiz_num + 1)
        quiz.save()

        quiz_temp = sub_course.quizzes.filter(order= 0)[0]
        quiz_temp.order = quiz_num
        quiz_temp.save()
    return redirect(reverse('course_Truong:sub_course_list', kwargs={'course_pk': course_pk}))