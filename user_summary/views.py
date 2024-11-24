from django.shortcuts import render
from certificate.models import Certificate
from django.core.paginator import Paginator
from ai_insights.models import AIInsights
from performance_analytics.models import PerformanceAnalytics
from django.shortcuts import render
from module_group.models import ModuleGroup, Module
from course.models import Course, Enrollment
from quiz.models import Quiz, StudentQuizAttempt
from user.models import User
from collections import Counter

def user_summary(request):
    user = request.user  
    certificates = Certificate.objects.filter(user=user.id)
    ai_insights = AIInsights.objects.filter(user=user.id)
    analytics = PerformanceAnalytics.objects.filter(user=user.id)
    paginator = Paginator(certificates, 2) 

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)


    module_groups = ModuleGroup.objects.all()
    modules = Module.objects.all()
    course = Enrollment.objects.filter(student=request.user)
    _dict = {"courses":None,
            "Percent":None}
    list = []
    for i in course:
        total, attempts = calculate(request.user, i.course.id)
        dict_ = dict(_dict)
        if total == 0:
            dict_['courses'] = i
            dict_['Percent'] = 0
        else:
            dict_['courses'] = i
            dict_['Percent'] = attempts / total * 100
        list.append(dict_)

    context = {
        'page_obj': page_obj,
        'certificates':certificates,
        'ai_insights':ai_insights,
        'analytics':analytics,
        'module_groups': module_groups,
        'modules': modules,
        'courses': list,
        'course_count':len(list),
        'user': request.user
    }
    return render(request, 'user_summary.html', context)

def calculate(user_id, course_id):
    quizzes = Quiz.objects.filter(course=course_id).count()
    attempts = len(Counter(set(
        StudentQuizAttempt.objects.filter(user=user_id, quiz__course=course_id).values_list('quiz_id', flat=True)
        )))
    return quizzes, attempts