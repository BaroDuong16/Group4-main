from django import forms
from django.contrib.auth.forms import AuthenticationForm

class ExcelImportForm(forms.Form):
    excel_file = forms.FileField(label="Upload Excel File")