from django import forms
from .models import Submission, Exercise

class SubmissionForm(forms.ModelForm):
    class Meta:
        model = Submission
        fields = ['code']
        widgets = {
            'code': forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'id': 'code-editor'}),  # Thêm id 'code-editor'
        }



class ExerciseForm(forms.ModelForm):
    class Meta:
        model = Exercise
        fields = ['title', 'description', 'language','test_cases']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'language': forms.Select(attrs={'class': 'form-control'}),
            'test_cases': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
        }