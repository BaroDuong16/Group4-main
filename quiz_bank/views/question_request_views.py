from django.shortcuts import render, redirect
from django.urls import reverse
from quiz.models import Quiz, Question, AnswerOption
from ..models import *
from ..forms import *
from django.forms.models import modelformset_factory


def delete_question(request, course_id, question_id):
    question = QuizBank.objects.get(id=question_id)
    answer = Answer.objects.filter(question_id=question_id)
    if request.method == 'POST':
        question.delete()
        return redirect(reverse('quiz_bank:quiz_bank_course',kwargs={'course_id':course_id}))
    return render(request, 'question_delete.html', {'question': question,
                                                        'answer': answer, 
                                                        'course_id':course_id})

def edit_question(request, course_id, question_id):
    question = QuizBank.objects.get(id=question_id)
    answer = Answer.objects.filter(question_id=question_id)
    AnswerFormset = modelformset_factory(model=Answer, form=AnswerForm, extra=0)
    if request.method == 'POST':
        answer_formset = AnswerFormset(request.POST, queryset=answer)
        question_form = QuestionForm(request.POST, instance=question)
        if all([answer_formset.is_valid(), question_form.is_valid()]):
            question_form.save()
            answer_formset.save()
            return redirect(reverse('quiz_bank:quiz_bank_course',kwargs={'course_id':course_id}))
    else:
        answer_formset = AnswerFormset(queryset=answer)
        question_form = QuestionForm(instance=question)
    return render(request, 'edit_question.html', {'answer_formset':answer_formset,
                                                  'question_form':question_form,
                                                  'course_id':course_id})