from django import forms
from .models import PerformanceAnalytics



class PerformanceAnalyticsForm(forms.ModelForm):
    class Meta:
        model = PerformanceAnalytics
        fields = ['average_score', 'completion_rate', 
                 'predicted_performance', 'user_id', 'course_id']


        # widgets = {
        #     'certificate_id': forms.NumberInput(),
        #     'user_id': forms.NumberInput(),
        #     'course_id': forms.NumberInput(),
        #     'issue_date': forms.DateInput(attrs={'class': 'form-control'}),
        #     'certificate_url': forms.TextInput(attrs={'class': 'form-control'}),
        # }
# class PerformanceAnalyticsForm(forms.ModelForm):
#     class Meta:
#         model = PerformanceAnalytics
#         fields = ['average_score', 'completion_rate', 
#                  'predicted_performance'] 