from django.contrib import admin
from .models import InstructorFeedback, CourseFeedback, TrainingProgramFeedback

admin.site.register(InstructorFeedback)
admin.site.register(CourseFeedback)
admin.site.register(TrainingProgramFeedback)