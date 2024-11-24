from django import forms

class BackupForm(forms.Form):
    confirm_backup = forms.BooleanField(label="Confirm Backup")

class RestoreForm(forms.Form):
    backup_file = forms.FileField(label="Select a backup file")

# forms.py
from django import forms

class SearchForm(forms.Form):
    search_query = forms.CharField(
        max_length=100,
        required=False,
        label="",
        widget=forms.TextInput(
            attrs={
                'class': 'form-control mr-sm-2',
                'placeholder': 'Search by file name',
            }
        )
    )
