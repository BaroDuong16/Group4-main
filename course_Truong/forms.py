from django import forms
from .models import *

class Course_Form(forms.ModelForm):
    class Meta:
        model = NewCourse
        fields = ['course_name', 'description', 'image']


class Quiz_Form(forms.ModelForm):
    class Meta:
        model = Quiz
        fields = ['quiz_title', 'quiz_description', 'total_mark', 'mark_to_pass']


class Question_Form(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['question_text', 'question_type', 'points']


class Answer_Option_Form(forms.ModelForm):
    class Meta:
        model = Answer_Option
        fields = ['option_text', 'is_correct']

class Sub_Course_Form(forms.ModelForm):
    class Meta:
        model = Sub_Course
        fields = ['title']


class Module_Form(forms.ModelForm):
    class Meta:
        model = Module
        fields = ['title']


class Sub_Module_Form(forms.ModelForm):
    class Meta:
        model = Sub_Module
        fields = ['title', 'video_url', 'html_content']

        widgets = {
            'video_url': forms.Textarea(attrs={'rows': 1}),
            'html_content': forms.Textarea(attrs={'rows': 20}),
        }


class Image_Form(forms.ModelForm):
    class Meta:
        model = Image
        fields = ['image']