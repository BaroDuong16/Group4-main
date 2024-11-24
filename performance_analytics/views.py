from django.shortcuts import render
from .models import PerformanceAnalytics
from user.models import User
from django.core.paginator import Paginator

def performance_analytics_summary(request):
    user = request.user  
    analytics = PerformanceAnalytics.objects.filter(user=user.id)
    paginator = Paginator(analytics,3)
    page_nummber = request.GET.get('page')
    page_obj = paginator.get_page(page_nummber)

    context = {
        'page_obj':page_obj,
    }
    return render(request, 'performance_analytics_summary.html', context)
