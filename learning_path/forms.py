from django import forms
from .models import LearningPath, Step
from django.contrib.auth import get_user_model  # Import the user model

User = get_user_model()  # Get the user model

class LearningPathForm(forms.ModelForm):
    class Meta:
        model = LearningPath
        fields = ['title', 'description', 'creator']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
            'creator': forms.Select(attrs={'class': 'form-control'}),  # Dropdown for creator
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)  # Get the user from kwargs
        super().__init__(*args, **kwargs)
        if user:
            self.fields['creator'].queryset = User.objects.all()  # Set queryset for the creator field
            self.fields['creator'].initial = user  # Set the initial value to the current user


class StepForm(forms.ModelForm):
    class Meta:
        model = Step
        fields = ['title', 'description', 'sequence', 'courses']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
            'sequence': forms.NumberInput(attrs={'class': 'form-control'}),
            'courses': forms.SelectMultiple(attrs={'class': 'form-control'}),  # Multi-select for courses
        }
