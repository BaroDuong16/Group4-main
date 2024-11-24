from django.db import models
# from django.contrib.auth.models import User  # Assuming you are using Django's built-in User model\
from user.models import User

class AnalyticsReport(models.Model):
    report_id = models.AutoField(primary_key=True)
    report_date = models.DateTimeField(auto_now_add=True)  # Automatically set the current date/time
    report_type = models.CharField(max_length=50)
    report_data = models.JSONField(null=True, blank=True)  # Django has support for JSONField
    generated_by =  models.ForeignKey(User,on_delete=models.CASCADE, null=True)

    def __str__(self):
        return f"{self.report_type} Report - {self.report_date}"
