from django.db import models

# Create your models here.
class Assignment(models.Model):
    assignment_id = models.IntegerField(primary_key=True,null=False)
    assignment_name = models.CharField(max_length=100)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()

    def __str__(self):
        return self.assignment_name