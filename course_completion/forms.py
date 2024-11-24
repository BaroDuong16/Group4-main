from django import forms
from .models import CourseCompletion

class CourseCompletionForm(forms.ModelForm):
    class Meta:
        model = CourseCompletion
        fields = ['user_id', 'course_id']

    