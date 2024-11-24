from django.shortcuts import render, redirect
from django.urls import reverse
from django.http import HttpResponse, JsonResponse, HttpRequest
from quiz.models import Quiz, Question, AnswerOption
from course.models import Course
from copy import deepcopy
import json
from ..functions import get_random
from ..forms import *
from ..models import *

# Create your views here.
def quiz_bank_view(request):
    courses = Course.objects.all()
    course_question_list = list()
    for course in courses:
        course_question = dict({
            'id': course.id,
            'code':course.course_code,
            'name':course.course_name,
            'question_count':len(QuizBank.objects.filter(course_id=course.id))
        })
        course_question_list.append(course_question)

    if request.method == 'POST':
        form = QuestionCourseForm(request.POST)
        if form.is_valid():
            course_name = form.cleaned_data['course']
            print(course_name)
            # request.session['form_data'] = form.cleaned_data
            try:
                try:
                    course_id = Course.objects.get(course_code=course_name).id
                except:
                    course_id = Course.objects.get(course_name=course_name).id
            except:
                return render(request, 'quiz_bank_view.html', {'form':form, 'courses':course_question_list})
            url = f'show/{course_id}/'
            return redirect(url)
    else:
        if 'form_data' in request.session:
            form = QuestionCourseForm(request.session['form_data'])
        else:
            form = QuestionCourseForm()
    return render(request, 'quiz_bank_view.html', {'form':form, 'courses':course_question_list})
    
def quiz_bank_course(request, course_id):
    course = Course.objects.get(id=course_id)
    filter_form = FilterByQuestionTypeForm(request.GET)
    form = NumberForm()
    if filter_form.is_valid():
        question_queryset = Answer.objects.filter(question__course_id=course_id, 
                                                  question__question_type=filter_form.cleaned_data['filter_by'])
    else:
        question_queryset = Answer.objects.filter(question__course_id=course_id)
    if len(question_queryset) != 0:
        questions_list = list()

        for question in question_queryset:
            question_context = question.question.question_text

            question_dict = dict({
                'question':question_context,
                'answer':list(),
                'key':list(),
                'id':None,
                'question_type':question.question.question_type
            })
            
            question_dict['id'] = question.question.id
            question_dict['answer'].append(question.option_text)
            if question.is_correct:
                question_dict['key'].append(question.option_text)

            questions_list.append(question_dict)
        
        def merge_dictionaries(dictionaries):
            merged_dict = {}
            for dictionary in dictionaries:
                id = dictionary['id']
                question = dictionary['question']
                answer = dictionary['answer']
                key = dictionary['key']
                question_type = dictionary['question_type']

                if question not in merged_dict:
                    merged_dict[question] = {'answer': [], 'key': list(), 'id':None}

                merged_dict[question]['answer'].extend(answer)
                merged_dict[question]['key'].extend(key)
                if id is not None:
                    merged_dict[question]['id'] = id
                if question_type is not None:
                    merged_dict[question]['question_type'] = question_type

            return list(merged_dict.items())

        questions_list = merge_dictionaries(questions_list)

        final_question_list = list()

        for question in questions_list:
            processed_question = (question[0], question[1]['answer'], question[1]['key'], question[1]['id'], question[1]['question_type'])
            final_question_list.append(dict(zip(["question", "options", "correct", "id", 'question_type'], processed_question)))

        if request.method == "POST":
            form = NumberForm(request.POST)
            number_of_questions = int(form.data['number_of_questions'])
            if number_of_questions < 1:
                return render(request, 'quiz_bank_course.html', context={'course': course, 
                                                                        'question_list': final_question_list, 
                                                                        'question_count':len(final_question_list), 
                                                                        'is_shown':True, 
                                                                        'is_valid':False,
                                                                        'course_id':course_id,
                                                                        'form':form})
            request.session['json_data'] = get_random(course_id, number_of_questions)
            request.session['json_data'] = deepcopy(request.session['json_data'])
            request.session['before'] = 'show'
            return redirect(reverse('quiz_bank:random_question_view', 
                                    kwargs={'course_id':course_id,
                                            'number_of_questions': number_of_questions}))
        else:
            return render(request, 'quiz_bank_course.html', context={'course': course, 
                                                                        'question_list': final_question_list, 
                                                                        'question_count':len(final_question_list), 
                                                                        'is_shown':True, 
                                                                        'is_valid':True,
                                                                        'course_id':course_id,
                                                                       'form':form,
                                                                       'filter_form': filter_form})
    else:    
        return render(request, 'quiz_bank_course.html', {'form':form,
                                                        'course': course, 
                                                        'is_shown':False, 
                                                        'course_id':course_id,
                                                        'filter_form': filter_form})
    
def random_question_view(request, course_id:int, number_of_questions:int):
    """
    _summary_
    Args:
        request (_HttpRequest_): _HTTP_Request_
        course_id (int): __
        number_of_questions (int): __

    To access to this view, simply use this url via namespace:

        'quiz_bank:random_question_view' 

        Required **kwarg: {course_id (int):..., 
                           number_of_questions (int):...}

    If you are trying to access to this view via Adding quiz, please add the code below (right before sending HttpRequest):

        request.session['before'] = 'add_quiz'
    """    
    def rendering(request, course_id, number_of_questions, question_list, course, is_add):
        if request.method == "POST":
            if 'reload' in request.POST:
                request.session['json_data'] = get_random(course_id, number_of_questions)
                request.session['json_data'] = deepcopy(request.session['json_data'])
                return render(request, 'random_question_view.html', context={'question_list':request.session['json_data'],
                                                                             'course': course,
                                                                             'is_add':is_add}) 
            elif 'export-json' in request.POST:
                if is_add:
                    request.session['json_data'] = deepcopy(json.dumps(question_list))
                    return redirect('quiz:quiz_add')
                else:
                    response = JsonResponse(question_list, safe=False)
                    response['Content-Disposition'] = 'attachment; filename="random_questions.json"'
                    return response
        print(question_list)
        return render(request, 'random_question_view.html', context={'question_list': question_list,
                                                                     'course': course,
                                                                     'is_add': is_add})   
    
    course = Course.objects.get(id=course_id)
    if 'json_data' in request.session:
        if request.session.get('before') == 'quiz_add':
            if type(request.session['json_data']) == str:
                json_data = deepcopy(json.loads(request.session['json_data']))
            else:
                json_data = deepcopy(request.session['json_data'])
        else:
            json_data = deepcopy(request.session['json_data'])
    else:
        request.session['json_data'] = get_random(course_id, number_of_questions)
        json_data = deepcopy(request.session['json_data'])
    before = request.session.get('before')

    match before:
        case 'quiz_add':
            is_add = True       
            return rendering(request, course_id, number_of_questions, json_data, course, is_add)   
        case _:
            is_add = False
            return rendering(request, course_id, number_of_questions, json_data, course, is_add)           