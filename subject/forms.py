from django import forms
from .models import Subject, Material, Lesson

# Form for creating and editing subjects
class SubjectForm(forms.ModelForm):
    class Meta:
        model = Subject
        fields = ['name', 'code', 'description']  # 'code' field added

# Form for uploading materials
class MaterialUploadForm(forms.ModelForm):
    class Meta:
        model = Material
        fields = ['lesson', 'material_type', 'file', 'google_drive_link']  # Updated to use lesson and google_drive_link

    material_type = forms.ChoiceField(choices=Material.MATERIAL_TYPE_CHOICES, widget=forms.RadioSelect)
    
    # Use a simple FileInput for file uploads
    file = forms.FileField(required=False)  # Made file optional since google_drive_link can also be used
    google_drive_link = forms.URLField(required=False, widget=forms.URLInput(attrs={'placeholder': 'Google Drive link (optional)'}))
