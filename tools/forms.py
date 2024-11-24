from django import forms
from .fields import MultipleFilesField
import os
class ExcelUploadForm(forms.Form):
    files = MultipleFilesField(required=True)
