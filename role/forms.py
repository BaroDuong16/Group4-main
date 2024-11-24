from django import forms
from .models import Role

class RoleForm(forms.ModelForm):
    class Meta:
        model = Role
        fields = ['role_name']
        widgets = {
            'role_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter role name'
            }),
        }

class ExcelImportForm(forms.Form):
    excel_file = forms.FileField(label="Upload Excel File")