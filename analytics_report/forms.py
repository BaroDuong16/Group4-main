from django import forms
from .models import AnalyticsReport

# Form for creating and editing users
class AnalyticsReportForm(forms.ModelForm):
    class Meta:
        model = AnalyticsReport
        fields = ['report_id', 'report_type', 'report_data', 'generated_by']
        exclude = ['report_date']
        widgets = {
            'report_data': forms.Textarea(attrs={'required': False}),  # Đảm bảo không bắt buộc
        }

