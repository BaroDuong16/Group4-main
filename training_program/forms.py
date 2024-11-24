from django import forms
from training_program.models import TrainingProgram
from subject.models import Subject  # Ensure this import is present

# Form for creating and editing training programs
class TrainingProgramForm(forms.ModelForm):
    subjects = forms.ModelMultipleChoiceField(
        queryset=Subject.objects.all(),
        widget=forms.CheckboxSelectMultiple,  # Use a checkbox widget for multiple selection
        required=False
    )

    class Meta:
        model = TrainingProgram
        fields = ['program_name', 'program_code', 'description', 'subjects']




