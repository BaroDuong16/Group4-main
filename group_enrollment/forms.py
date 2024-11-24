# enrollment/forms.py
from django import forms
from course.models import Enrollment, Course
from user.models import User

class EnrollmentForm(forms.ModelForm):
    class Meta:
        model = Enrollment
        fields = ['course']
        widgets = {
            'course': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)  # Get the user from kwargs
        super().__init__(*args, **kwargs)
        
        # Filter queryset: only published courses that the user hasn't enrolled in
        if user:
            enrolled_courses = Enrollment.objects.filter(student=user).values_list('course_id', flat=True)
            self.fields['course'].queryset = Course.objects.filter(
                published=True
            ).exclude(id__in=enrolled_courses)


class AdminEnrollmentForm(forms.Form):
    course = forms.ModelChoiceField(queryset=Course.objects.all(), required=True)
    users = forms.ModelMultipleChoiceField(
        queryset=User.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=True,
    )