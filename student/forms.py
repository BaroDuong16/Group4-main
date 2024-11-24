from django import forms
from .models import Student

# Form for registering a new student
class StudentRegistrationForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['first_name', 'last_name', 'email', 'is_active']
