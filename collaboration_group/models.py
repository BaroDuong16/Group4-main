from django.db import models
from django.conf import settings
from course.models import Course

class CollaborationGroup(models.Model):
    group_name = models.CharField(max_length=255)
    # course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='collaboration_groups')
    courses = models.ManyToManyField(Course, related_name='collaboration_groups')  # Change course to course_name
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

class GroupFeedback(models.Model):
    group = models.ForeignKey(
        CollaborationGroup, on_delete=models.CASCADE, related_name="group_feedbacks"
    )
    submitted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="submitted_group_feedbacks"
    )
    group_engagement = models.IntegerField(choices=[(i, str(i)) for i in range(1, 6)])
    collaboration_quality = models.IntegerField(choices=[(i, str(i)) for i in range(1, 6)])
    goal_achievement = models.IntegerField(choices=[(i, str(i)) for i in range(1, 6)])
    comments = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def average_rating(self):
        return (self.group_engagement + self.collaboration_quality + self.goal_achievement) / 3.0

    def __str__(self):
        return f"Feedback for Group: {self.group.name} by {self.submitted_by.username}"
    
class MemberFeedback(models.Model):
    member = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="member_feedbacks"
    )
    group = models.ForeignKey(
        CollaborationGroup, on_delete=models.CASCADE, related_name="member_feedbacks"
    )
    submitted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="submitted_member_feedbacks"
    )
    teamwork = models.IntegerField(choices=[(i, str(i)) for i in range(1, 6)])
    reliability = models.IntegerField(choices=[(i, str(i)) for i in range(1, 6)])
    leadership = models.IntegerField(choices=[(i, str(i)) for i in range(1, 6)])
    communication = models.IntegerField(choices=[(i, str(i)) for i in range(1, 6)])
    comments = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def average_rating(self):
        return (self.teamwork + self.reliability + self.leadership + self.communication) / 4.0

    def __str__(self):
        return f"Feedback for Member: {self.member.username} in Group: {self.group.name}"