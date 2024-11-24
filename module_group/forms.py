from django import forms
from .models import Module, ModuleGroup
class ModuleGroupForm(forms.ModelForm):
    class Meta:
        model = ModuleGroup
        fields = ['group_name']

class ExcelImportForm(forms.Form):
    excel_file = forms.FileField(label="Upload Excel File")

class ModuleForm(forms.ModelForm):
    class Meta:
        model = Module
        fields = ['module_name', 'module_url', 'icon', 'module_group']
        widgets = {
            'module_group': forms.Select(attrs={'class': 'form-control'}),
            'icon': forms.TextInput(attrs={'class': 'form-control'}),
        }
