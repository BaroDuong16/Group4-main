from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.http import JsonResponse
from django.views import View

from exercises.models import Exercise

class Get_exercise_content(View):
    @method_decorator(login_required)
    def get(self, request, exercise_id):
        exercise = Exercise.objects.get(id=exercise_id)
        return JsonResponse({
            'title': exercise.title,
            'content': exercise.description  
        })