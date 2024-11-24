from django import forms

class QuestionGenerationForm(forms.Form):
    topic = forms.CharField(label="Enter a topic for the question", max_length=200)
