from django.db import models
from django.conf import settings
from course.models import Course

class CollaborationGroup(models.Model):
    group_name = models.CharField(max_length=255)
    # course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='collaboration_groups')
    courses = models.ManyToManyField(Course, related_name='collaboration_groups')  # Change from ForeignKey to ManyToManyField
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='collaboration_groups_created')

    def __str__(self):
        return self.group_name


class GroupMember(models.Model):
    group = models.ForeignKey(CollaborationGroup, on_delete=models.CASCADE, related_name='members')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='group_memberships')
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('group', 'user')

    def __str__(self):
        return f'{self.user.username} - {self.group.group_name}'
