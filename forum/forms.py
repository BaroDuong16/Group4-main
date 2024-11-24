from django import forms
from .models import ForumQuestion, ForumComment, Reply, Report

class ForumQuestionForm(forms.ModelForm):
    class Meta:
        model = ForumQuestion
        fields = ['course', 'title', 'content', 'image']
        widgets = {
            'image': forms.ClearableFileInput(attrs={'required': False}),
        }

class ForumCommentForm(forms.ModelForm):
    class Meta:
        model = ForumComment
        fields = ['content', 'image']
        widgets = {
            'image': forms.ClearableFileInput(attrs={'required': False}),
        }

class ReplyForm(forms.ModelForm):
    class Meta:
        model = Reply
        fields = ['content', 'image']
        widgets = {
            'image': forms.ClearableFileInput(attrs={'required': False}),
        }

class ReportForm(forms.ModelForm):
    class Meta:
        model = Report
        fields = ['reason']
        widgets = {
            'reason': forms.Textarea(attrs={'rows': 4}),
        }
