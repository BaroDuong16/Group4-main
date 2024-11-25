from django import forms
from .models import DiscussionThread,ThreadComments,ReportThread
from user.models import User  # Assuming you have a User model
from course.models import Course
class ThreadForm(forms.ModelForm):
    course = forms.ModelChoiceField(queryset=Course.objects.all(), required=True, empty_label="Select a course")

    class Meta:
        model = DiscussionThread
        fields = ['thread_title', 'thread_content','image', 'course']

class CommentForm(forms.ModelForm):
    class Meta:
        model = ThreadComments
        fields = ['comment_text','image']

class ThreadReportForm(forms.ModelForm):
    class Meta:
        model = ReportThread
        fields = ['reason','additional_comments']