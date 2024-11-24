from django.shortcuts import render
from module_group.models import ModuleGroup, Module
from course.models import Course, Enrollment
from quiz.models import Quiz, StudentQuizAttempt
from user.models import User
from collections import Counter
from django.core.paginator import Paginator
from .models import UserProgress

def user_progress_summary(request):
    module_groups = ModuleGroup.objects.all()
    modules = Module.objects.all()
    
    progress = UserProgress.objects.filter(user = request.user)
    completed = UserProgress.objects.filter(user=request.user, progress_percentage=100).count()

    percent_complete = round((completed / progress.count())*100,2) if progress.count() > 0 else 0

    paginator_pro = Paginator(progress, 4) 

    page_number_pro = request.GET.get('page')
    page_obj_pro = paginator_pro.get_page(page_number_pro)

    return render(request,'user_progress_summary.html',{'module_groups': module_groups,
                                             'modules': modules,
                                             'courses': page_obj_pro,
                                             'course_count':progress.count(),
                                             'completed': completed,
                                             'percent_complete':percent_complete,
                                             'user': request.user ,
                                             'page_obj_pro':page_obj_pro})

