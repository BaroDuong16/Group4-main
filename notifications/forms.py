from django import forms
from .models import Notification

class NotificationForm(forms.ModelForm):
    class Meta:
        model = Notification
        fields = ['title', 'message', 'file']  # Các trường của form
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter notification title'}),
            'message': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Enter notification message'}),
        }
        labels = {
            'title': 'Notification Title',
            'message': 'Notification Message',
        }

    def clean_file(self):
        file = self.cleaned_data.get('file', False)
        if file and file.size > 5*1024*1024:  # Giới hạn kích thước file: 5 MB
            raise forms.ValidationError("File size exceeds 5 MB limit.")
        return file