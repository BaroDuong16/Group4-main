from django.db import models
from django.contrib.auth.models import User  # Switch to User model
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.conf import settings

class UserActivityLog(models.Model):
    log_id = models.AutoField(primary_key=True)
    ACTIVITY_TYPES = [
        ('login', 'Login'),
        ('course_completion', 'Course Completion'),
        ('logout', 'Logout'),
        ('page_visit', 'Page Visit'),
    ]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    activity_type = models.CharField(max_length=100, choices=ACTIVITY_TYPES)
    activity_details = models.TextField(blank=True, null=True)
    activity_timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.username} - {self.activity_type} on {self.activity_timestamp}'

# Signal to log user login
@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    UserActivityLog.objects.create(user=user, activity_type='login', activity_details='User logged in.')

# Signal to log user logout
@receiver(user_logged_out)
def log_user_logout(sender, request, user, **kwargs):
    UserActivityLog.objects.create(user=user, activity_type='logout', activity_details='User logged out.')
