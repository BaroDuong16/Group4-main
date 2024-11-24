# certification/forms.py
from django import forms
from .models import Certification

class CertificationForm(forms.ModelForm):
    CHOICES = [
        ('upload', 'Upload File'), 
        ('html', 'Generate with HTML')
    ]

    # Field for choosing between file upload or HTML generation
    certificate_option = forms.ChoiceField(
        choices=CHOICES, 
        widget=forms.RadioSelect, 
        required=True,
        label="Certificate Option"
    )

    class Meta:
        model = Certification
        fields = ['name', 'course', 'description', 'awarded_date', 'awarded', 'certificate_option', 'certificate_file', 'generated_html_content']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter certificate name'}),
            'course': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Enter a brief description...'}),
            'awarded_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'awarded': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'certificate_file': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'generated_html_content': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Enter generated HTML content here...'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        option = cleaned_data.get('certificate_option')
        certificate_file = cleaned_data.get('certificate_file')
        generated_html_content = cleaned_data.get('generated_html_content')

        # Ensure that only one of the fields is filled based on the option chosen
        if option == 'upload' and not certificate_file:
            self.add_error('certificate_file', 'File upload is required when "Upload File" is selected.')

        if option == 'html' and not generated_html_content:
            self.add_error('generated_html_content', 'HTML content is required when "Generate with HTML" is selected.')

        return cleaned_data
