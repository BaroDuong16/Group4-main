from django import forms
from .models import Quiz, Question, AnswerOption, StudentAnswer
from .fields import MultipleFilesField

class QuizForm(forms.ModelForm):
    class Meta:
        model = Quiz
        fields = ['course', 'quiz_title', 'quiz_description', 'total_marks', 'time_limit', 'start_datetime', 'end_datetime', 'attempts_allowed']
        widgets = {
            'course': forms.Select(),
            'time_limit': forms.NumberInput(attrs={'min': 1}),
            'start_datetime': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'end_datetime': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'attempts_allowed': forms.NumberInput(attrs={'min': '1'}),
        }

class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['question_text', 'question_type', 'points']

class AnswerOptionForm(forms.ModelForm):
    class Meta:
        model = AnswerOption
        fields = ['option_text', 'is_correct']


class QuizAnswerForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.questions = kwargs.pop('questions')  # List of questions
        super(QuizAnswerForm, self).__init__(*args, **kwargs)
        
        for question in self.questions:
            if question.question_type == 'MCQ':
                # Create multiple-choice field
                choices = [(option.id, option.option_text) for option in question.answer_options.all()]
                self.fields[f'question_{question.id}'] = forms.ChoiceField(
                    label=question.question_text,
                    widget=forms.RadioSelect,
                    choices=[(option.id, option.option_text) for option in question.answer_options.all()],
                    required=True
                )
            elif question.question_type == 'TF':
                # Create true/false field
                self.fields[f'question_{question.id}'] = forms.ChoiceField(
                    label=question.question_text,
                    widget=forms.RadioSelect,
                    choices=[(True, 'True'), (False, 'False')]
                )
            elif question.question_type == 'TEXT':
                # Create text input field for text response
                self.fields[f'question_{question.id}'] = forms.CharField(
                    label=question.question_text,
                    widget=forms.Textarea(attrs={'rows': 4, 'cols': 40}),
                    required=True
                )

class ExcelUploadForm(forms.Form):
    files = MultipleFilesField(required=True)