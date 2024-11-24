from django.shortcuts import render
from module_group.models import ModuleGroup, Module
from course.models import Course
from django.core.paginator import Paginator
from .models import UserProgress, PerformanceAnalytics, AIInsights
import json
from .forms import AI_InsightsCourseForm
from assessments.models import StudentAssessmentAttempt, Assessment
# Create your views here.
module_groups = ModuleGroup.objects.all()
modules = Module.objects.all()
def user_progress(request):

    module_groups = ModuleGroup.objects.all()
    modules = Module.objects.all()
    
    progress = UserProgress.objects.filter(user = request.user)
    completed = UserProgress.objects.filter(user=request.user, progress_percentage=100).count()

    percent_complete = round((completed / progress.count())*100,2) if progress.count() > 0 else 0

    paginator_pro = Paginator(progress, 3) 

    page_number_pro = request.GET.get('page')
    page_obj_pro = paginator_pro.get_page(page_number_pro)

    return render(request,'user_progress.html',{'module_groups': module_groups,
                                             'modules': modules,
                                             'courses': page_obj_pro,
                                             'course_count':progress.count(),
                                             'completed': completed,
                                             'percent_complete':percent_complete,
                                             'user': request.user ,
                                             'page_obj_pro':page_obj_pro})


def performance_analytics(request):
    user = request.user  
    analytics = PerformanceAnalytics.objects.filter(user=user.id)
    # Annotate each PerformanceAnalytics object with total assessments and qualified attempts
    # Annotate each PerformanceAnalytics object with total assessments and qualified attempts
    for data in analytics:
        data.total_assessments = Assessment.objects.filter(course=data.course).count()
        data.qualified_attempts = 0
        assessments = Assessment.objects.filter(course=data.course)
        for data in analytics:
            data.total_assessments = Assessment.objects.filter(course=data.course).count()
            data.qualified_attempts = 0
            data.attempts = []
            assessments = Assessment.objects.filter(course=data.course)
            for assessment in assessments:
                qualifying_score = assessment.qualify_score
                qualified_attempts = StudentAssessmentAttempt.objects.filter(
                    user=data.user,
                    assessment=assessment,
                    score_ass__gte=qualifying_score
                ).values('assessment').distinct().count()
                data.qualified_attempts += qualified_attempts
                data.attempts.extend(StudentAssessmentAttempt.objects.filter(
                    user=data.user,
                    assessment=assessment,
                    # score_ass__gte=qualifying_score
                ))
            
    paginator = Paginator(analytics,4)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj':page_obj,
        'module_groups': module_groups,
        'modules': modules,
    }
    return render(request, 'performance_analytics.html', context)

def ai_insights(request):
    user = request.user      
    labels = ['Warning', 'Compliment', 'Info', 'Undefined']
    if request.method == 'POST':
        filter_form = AI_InsightsCourseForm(request.POST)
        if filter_form.is_valid():
            if filter_form.data['course'] == '':
                filter_form = AI_InsightsCourseForm()
                ai_insights = AIInsights.objects.filter(user=user.id).order_by('-created_at')
                ai_insights_count = len(list(ai_insights))

                warning = ai_insights.filter(insight_type='Warning')
                compliment = ai_insights.filter(insight_type='Compliment')
                info = ai_insights.filter(insight_type='Info')

                warning_count = len(list(warning))
                compliment_count = len(list(compliment))
                info_count = len(list(info))

                data = [warning_count, compliment_count, info_count, (ai_insights_count-warning_count-compliment_count-info_count)]
                paginator = Paginator(ai_insights, 4) 
                page_number = request.GET.get('page')
                page_obj = paginator.get_page(page_number)
                context = {
                    'page_ai_insights': page_obj,
                    'user': request.user,
                    'filter_form': filter_form,
                    'data': json.dumps(data),
                    'labels': json.dumps(labels),
                    'chart_name': 'All courses',
                    'is_valid': False
                    }
                return render(request, 'ai_insights_summary.html', context)
            ai_insights = AIInsights.objects.filter(user=user.id, course=filter_form.data['course']).order_by('-created_at')
            course = Course.objects.get(id=filter_form.data['course']).course_name
            ai_insights_count = len(list(ai_insights))

            warning = ai_insights.filter(insight_type='Warning')
            compliment = ai_insights.filter(insight_type='Compliment')
            info = ai_insights.filter(insight_type='Info')

            warning_count = len(list(warning))
            compliment_count = len(list(compliment))
            info_count = len(list(info))

            data = [warning_count, compliment_count, info_count, (ai_insights_count-warning_count-compliment_count-info_count)]
            paginator = Paginator(ai_insights, 4) 

            page_number = request.GET.get('page')
            page_obj = paginator.get_page(page_number)

            context = {
                'page_ai_insights': page_obj,
                'user': request.user,
                'filter_form': filter_form,
                'data': json.dumps(data),
                'labels': json.dumps(labels),
                'chart_name': course,
                'is_valid': True,
                'module_groups': module_groups,
                'modules': modules,
            }
            return render(request, 'ai_insights.html', context)
    else:
        filter_form = AI_InsightsCourseForm()

        ai_insights = AIInsights.objects.filter(user=user.id).order_by('-created_at')

        ai_insights_count = len(list(ai_insights))

        warning = ai_insights.filter(insight_type='Warning')
        compliment = ai_insights.filter(insight_type='Compliment')
        info = ai_insights.filter(insight_type='Info')

        warning_count = len(list(warning))
        compliment_count = len(list(compliment))
        info_count = len(list(info))

        data = [warning_count, compliment_count, info_count, (ai_insights_count-warning_count-compliment_count-info_count)]
        paginator = Paginator(ai_insights, 4) 
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        

        context = {
            'page_ai_insights': page_obj,
            'user': request.user,
            'filter_form': filter_form,
            'data': json.dumps(data),
            'labels': json.dumps(labels),
            'chart_name': 'All courses',
            'is_valid': True,
            'module_groups': module_groups,
            'modules': modules,
        }
    return render(request, 'ai_insights.html', context)
