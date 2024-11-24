from django.db import models
from django.conf import settings
from ckeditor.fields import RichTextField
from ckeditor_uploader.fields import RichTextUploadingField
from datetime import datetime
from django.utils import timezone
from django.template.loader import render_to_string

class Course(models.Model):
    course_name = models.CharField(max_length=255, unique=True)
    course_code = models.CharField(max_length=20, unique=True, blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    creator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_courses')
    instructor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='taught_courses')
    published = models.BooleanField(default=False)
    prerequisites = models.ManyToManyField('self', symmetrical=False, blank=True, related_name='is_prerequisite_for')
    tags = models.ManyToManyField('Tag', blank=True, related_name='courses')
    image = models.ImageField(upload_to='course_images/', null=True, blank=True)

    def __str__(self):
        return self.course_name

    def get_completion_percent(self, user):
        total_sessions = self.sessions.count()
        completed_sessions = SessionCompletion.objects.filter(session__course=self, user=user, completed=True).count()
        return (completed_sessions / total_sessions) * 100 if total_sessions > 0 else 0

    def check_and_generate_certification(self, user):
        from certification.models import Certification  # Import within the method
        # Count total sessions and completed sessions
        total_sessions = self.sessions.count()
        completed_sessions = SessionCompletion.objects.filter(course=self, user=user, completed=True).count()

        if total_sessions == completed_sessions:
            # Generate certification if it doesn't exist already
            if not Certification.objects.filter(course=self, user=user).exists():
                # Define context variables for the template
                context = {
                    'recipient_name': user.username,
                    'course_name': self.course_name,
                    'description': "Successfully completed the course.",
                    'awarded_date': timezone.now().strftime('%Y-%m-%d'),
                    'year': timezone.now().year,
                }

                # Render the certificate template to a string
                generated_html_content = render_to_string('certification/certificate_template.html', context)

                # Create and save the certification
                certification = Certification.objects.create(
                    name=f"{self.course_name} Completion Certificate",
                    course=self,
                    user=user,
                    awarded_date=timezone.now(),
                    awarded=True,
                    generated_html_content=generated_html_content
                )
                certification.save()

class Topic(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(max_length=255)
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name='tag_set')  # Change 'tags' to 'tag_set'

    class Meta:
        unique_together = ('name', 'topic')

    def __str__(self):
        return self.name

class Session(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='sessions', null=True)
    name = models.CharField(max_length=255)
    order = models.PositiveIntegerField()  # Order of appearance

    def __str__(self):
        return self.name

class Enrollment(models.Model):
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='enrollments')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments')
    date_enrolled = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('student', 'course')

    def __str__(self):
        return f"{self.student} enrolled in {self.course}"

class CourseMaterial(models.Model):
    MATERIAL_TYPE_CHOICES = [
        ('assignments', 'Assignments'),
        ('labs', 'Labs'),
        ('lectures', 'Lectures'),
        ('references', 'References'),  # New material type
        ('assessments', 'Assessments'),
    ]
    session = models.ForeignKey(Session, on_delete=models.CASCADE, related_name='materials', null=True)
    material_id = models.PositiveIntegerField()  # Make sure this uniquely identifies the material
    material_type = models.CharField(max_length=20, choices=MATERIAL_TYPE_CHOICES)
    order = models.PositiveIntegerField()  # Order of appearance
    title = models.CharField(max_length=255)

    def __str__(self):
        return f'session id: {self.session.id}   title: {self.title}'

    class Meta:
        ordering = ['order']

class ReadingMaterial(models.Model):
    material = models.ForeignKey(CourseMaterial, on_delete=models.CASCADE, related_name='materials', null=True)
    content = RichTextUploadingField()  # Use RichTextUploadingField for HTML content with file upload capability
    title = models.CharField(max_length=255)
    pdf_file = models.FileField(upload_to='pdf_files/', null=True, blank=True)  # PDF upload field
    def __str__(self):
        return self.title


class Completion(models.Model):
    session = models.ForeignKey(Session, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    material = models.ForeignKey(CourseMaterial, on_delete=models.CASCADE, null=True, blank=True)
    completed = models.BooleanField(default=False)

    class Meta:
        unique_together = ('session', 'material', 'user')

    def __str__(self):
        return f"Completion for {self.material} in {self.session}"


class SessionCompletion(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    session = models.ForeignKey(Session, on_delete=models.CASCADE)
    completed = models.BooleanField(default=False)

    class Meta:
        unique_together = ('course', 'user', 'session')  # Ensures a user can only complete a session once

    def __str__(self):
        return f"{self.user} completed session: {self.session.name}"

def mark_session_complete(course, user, session):
    # Count the total materials in the session
    total_materials = session.materials.count()

    # Count completed materials by checking the Completion model
    completed_materials = Completion.objects.filter(session=session, user=user, completed=True).count()

    # Check if all materials are completed
    if total_materials == completed_materials:
        # Mark the session as complete in the SessionCompletion model
        SessionCompletion.objects.update_or_create(
            course=course,
            user=user,
            session=session,
            defaults={'completed': True}
        )

        # After marking session complete, check if the course is fully complete
        course.check_and_generate_certification(user)


# def mark_session_complete(course, user, session):
#     # Count the total materials in the session
#     total_materials = session.materials.count()

#     # Count completed materials by checking the Completion model
#     completed_materials = Completion.objects.filter(session=session, user=user, completed=True).count()

#     # Check if all materials are completed
#     if total_materials == completed_materials:
#         # Mark the session as complete in the SessionCompletion model
#         SessionCompletion.objects.update_or_create(
#             user=user,
#             session=session,
#             defaults={'completed': True}
#         )

class UserCourseProgress(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='course_progress', on_delete=models.CASCADE)  # Thêm related_name
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    progress_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    last_accessed = models.DateTimeField(auto_now=True)  # Cập nhật thời gian truy cập gần nhất

    class Meta:
        unique_together = ('user', 'course')

    def __str__(self):
        return f"{self.user} - {self.course} - {self.progress_percentage}%"