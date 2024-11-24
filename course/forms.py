from django import forms
from .models import *
from django.contrib.auth import get_user_model
#from ckeditor.widgets import CKEditorWidget
from .models import ReadingMaterial
User = get_user_model()

# Form for creating and editing courses
# forms.py

class CourseForm(forms.ModelForm):
    creator = forms.ModelChoiceField(queryset=User.objects.all(), required=False, empty_label="Select Creator")
    instructor = forms.ModelChoiceField(queryset=User.objects.all(), required=False, empty_label="Select Instructor")
    prerequisites = forms.ModelMultipleChoiceField(queryset=Course.objects.all(),required=False,widget=forms.CheckboxSelectMultiple)
    integer_field = forms.IntegerField(required=False)  # mới thêm
    tags = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple
    )

    class Meta:
        model = Course
        fields = ['course_name', 'course_code', 'description', 'creator', 'instructor', 'prerequisites', 'tags', 'image']  # sửa lại

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['image'].required = False

class SessionForm(forms.ModelForm):
    session_name = forms.CharField(max_length=50, required=False, label="Session Name")
    session_quantity = forms.IntegerField(min_value=1, required=False, label="Number of Sessions")
    class Meta:
        model = Session
        fields = ['name', 'order', 'course']

class EnrollmentForm(forms.ModelForm):
    class Meta:
        model = Enrollment
        fields = []

class CourseSearchForm(forms.Form):
    query = forms.CharField(max_length=255, required=False, label='Research Course')

class ExcelImportForm(forms.Form):
    excel_file = forms.FileField(label="Upload Excel File")


class CompletionForm(forms.ModelForm):
    class Meta:
        model = Completion
        fields = ['completed', 'material']


# class ReadingMaterialForm(forms.ModelForm):
#     class Meta:
#         model = ReadingMaterial
#         fields = ['title', 'content', 'pdf_file']  # Include pdf_file for file uploads

class ReadingMaterialForm(forms.ModelForm):
    #content = forms.CharField(widget=CKEditorWidget(config_name='default'))
    class Meta:
        model = ReadingMaterial
        fields = ['title', 'content', 'material', 'pdf_file']

class UploadFileForm(forms.Form):
    file = forms.FileField()

class TopicForm(forms.ModelForm):
    class Meta:
        model = Topic
        fields = ['name']

class TagForm(forms.ModelForm):
    class Meta:
        model = Tag
        fields = ['name', 'topic']

class ReadingMaterialEditForm(forms.ModelForm):
    class Meta:
        model = ReadingMaterial
        fields = ['title', 'content']
