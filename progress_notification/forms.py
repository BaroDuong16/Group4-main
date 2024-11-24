from django import forms
from .models import ProgressNotification

# Form for creating and editing users
class ProgressNotificationForm(forms.ModelForm):
    class Meta:
        model = ProgressNotification
        fields = ['user', 'course', 'notification_message']

class ExcelImportForm(forms.Form):
    excel_file = forms.FileField(label="Upload Excel File")