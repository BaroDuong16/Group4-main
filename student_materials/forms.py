# forms.py
from django import forms
from subject.models import Subject, Material  # Assuming you have these models

class MaterialSelectionForm(forms.Form):
    subject = forms.ModelChoiceField(queryset=Subject.objects.all(), label='Select Subject')
    material_type = forms.ChoiceField(choices=[
        ('assignments', 'Assignments'),
        ('labs', 'Labs'),
        ('lectures', 'Lectures'),
        ('references', 'References'),
    ], label='Select Material Type')
