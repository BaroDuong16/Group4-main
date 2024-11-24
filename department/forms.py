from django import forms
from .models import Location, Department
from user.models import User
from course.models import Course

class LocationForm(forms.ModelForm):
    class Meta:
        model = Location
        fields = ['name', 'address']

class DepartmentForm(forms.ModelForm):
    users = forms.ModelMultipleChoiceField(
        queryset=User.objects.all(),
        widget=forms.CheckboxSelectMultiple,  # Sử dụng checkbox
        required=False
    )
    courses = forms.ModelMultipleChoiceField(
        queryset=Course.objects.all(),
        widget=forms.CheckboxSelectMultiple,  # Sử dụng checkbox
        required=False
    )

    class Meta:
        model = Department
        fields = ['name', 'location', 'users', 'courses']
