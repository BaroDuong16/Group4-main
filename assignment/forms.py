from django import forms
from .models import Assignment
class AssignmentForm(forms.ModelForm):
    class Meta:
        model = Assignment
        fields = ['assignment_id','assignment_name', 'start_date', 'end_date']
        widgets = {
            'assignment_id': forms.NumberInput(),
            'assignment_name': forms.TextInput(attrs={'class': 'form-control'}),
            'start_date': forms.DateInput(attrs={'class': 'form-control'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control'}),
        }