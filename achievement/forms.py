from django import forms
from .models import AIInsights

# Form for creating and editing users
class AI_InsightsForm(forms.ModelForm):
    class Meta:
        model = AIInsights
        fields = ['user', 'course', 'insight_text', 'insight_type']
        labels = {
            'insight_type': 'Insight Type (Either "Warning", "Compliment" or "Info" is prefered)'
        }

class ExcelImportForm(forms.Form):
    excel_file = forms.FileField(label="Upload Excel File")

class AI_InsightsCourseForm(forms.ModelForm):
    class Meta:
        model = AIInsights
        fields = ['course']
        labels = {
            'course': 'Choose a course to filter'
        }
