from django.db import models
from django.conf import settings
from course.models import Course  # Assuming Course is in the course app
from training_program.models import TrainingProgram  # Assuming Training Program model exists

class InstructorFeedback(models.Model):
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    instructor = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="instructor_feedback", on_delete=models.CASCADE)

    course_knowledge = models.IntegerField(choices=[(i, str(i)) for i in range(1, 6)])
    communication_skills = models.IntegerField(choices=[(i, str(i)) for i in range(1, 6)])
    approachability = models.IntegerField(choices=[(i, str(i)) for i in range(1, 6)])
    engagement = models.IntegerField(choices=[(i, str(i)) for i in range(1, 6)])
    professionalism = models.IntegerField(choices=[(i, str(i)) for i in range(1, 6)])

    # Automatically calculated mean rating
    def average_rating(self):
        return (self.course_knowledge + self.communication_skills +
                self.approachability + self.engagement + self.professionalism) / 5.0

    comments = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

class CourseFeedback(models.Model):
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)

    course_material = models.IntegerField(choices=[(i, str(i)) for i in range(1, 6)])
    clarity_of_explanation = models.IntegerField(choices=[(i, str(i)) for i in range(1, 6)])
    course_structure = models.IntegerField(choices=[(i, str(i)) for i in range(1, 6)])
    practical_applications = models.IntegerField(choices=[(i, str(i)) for i in range(1, 6)])
    support_materials = models.IntegerField(choices=[(i, str(i)) for i in range(1, 6)])

    helpful_rate = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='helpful_rate', blank=True)

    # Automatically calculated mean rating
    def average_rating(self):
        return (self.course_material + self.clarity_of_explanation +
                self.course_structure + self.practical_applications + self.support_materials) / 5.0

    comments = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

class TrainingProgramFeedback(models.Model):
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    training_program = models.ForeignKey(TrainingProgram, on_delete=models.CASCADE)

    relevance = models.IntegerField(choices=[(i, str(i)) for i in range(1, 6)])
    organization = models.IntegerField(choices=[(i, str(i)) for i in range(1, 6)])
    learning_outcomes = models.IntegerField(choices=[(i, str(i)) for i in range(1, 6)])
    resources = models.IntegerField(choices=[(i, str(i)) for i in range(1, 6)])
    support = models.IntegerField(choices=[(i, str(i)) for i in range(1, 6)])

    # Automatically calculated mean rating
    def average_rating(self):
        return (self.relevance + self.organization +
                self.learning_outcomes + self.resources + self.support) / 5.0

    comments = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
