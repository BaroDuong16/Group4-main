from django.shortcuts import HttpResponse,render, get_object_or_404, redirect
from .models import CourseCompletion
from .forms import CourseCompletionForm

# Create your views here.

def course_completion_list(request):
    try:
        course = CourseCompletion.objects.all()
        return render(request, 'CourseCompletion_list.html', {'courses':course})
    except Exception as e:
        return HttpResponse(f'error: {e}')
def Completed(request):
    pass