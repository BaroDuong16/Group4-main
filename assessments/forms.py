from django import forms
from .models import AssessmentType, Assessment, StudentAssessmentAttempt

class AssessmentTypeForm(forms.ModelForm):
    class Meta:
        model = AssessmentType
        fields = ['type_name']

class AssessmentForm(forms.ModelForm):
    class Meta:
        model = Assessment
        fields = ['title', 'course', 'assessment_type', 'total_score', 'qualify_score', 'time_limit', 'exercises', 'questions']#'due_date', 
        widgets = {
            # 'due_date': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter course title'}),
            'course': forms.Select(attrs={'class': 'form-control', 'style': 'width: 100%;'}),
            'assessment_type': forms.Select(attrs={'class': 'form-control', 'placeholder': 'Select assessment type'}),
            'total_score': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter total score'}),
            'qualify_score': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter minimum score to qualify'}),
            'time_limit': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter time limit for assessment'}),
            'exercises': forms.CheckboxSelectMultiple(),
            'questions': forms.CheckboxSelectMultiple(),
        }
    


class InviteCandidatesForm(forms.Form):
    emails = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control w-100',  # Bootstrap class for full-width textarea
            'rows': 5,  # Adjust the height of the textarea
            'placeholder': 'Enter email addresses separated by commas...',
        }),
        help_text="Enter email addresses separated by commas."
    )



class AssessmentAttemptForm(forms.ModelForm):
    class Meta:
        model = StudentAssessmentAttempt
        fields = ['score_quiz', 'score_ass', 'note']
