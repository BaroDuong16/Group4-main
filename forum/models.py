from django.db import models
from django.conf import settings
from course.models import Course

class ForumQuestion(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    content = models.TextField()
    image = models.ImageField(upload_to='forum_images/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    likes = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='question_likes', blank=True)
    dislikes = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='question_dislikes', blank=True)

    def __str__(self):
        return self.title

class ForumComment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    question = models.ForeignKey(ForumQuestion, related_name='comments', on_delete=models.CASCADE)
    content = models.TextField()
    image = models.ImageField(upload_to='comment_images/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    likes = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='comment_likes', blank=True)
    dislikes = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='comment_dislikes', blank=True)

    def __str__(self):
        return f'Comment by {self.user.username}'

class Reply(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField()
    image = models.ImageField(upload_to='reply_images/', null=True, blank=True)
    comment = models.ForeignKey(ForumComment, related_name='replies', null=True, blank=True, on_delete=models.CASCADE)
    parent_reply = models.ForeignKey('self', null=True, blank=True, related_name='children', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    likes = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='reply_likes', blank=True)
    dislikes = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='reply_dislikes', blank=True)

    def __str__(self):
        return f'Reply by {self.user.username}'

    def is_reply(self):
        return self.parent_reply is not None

class Report(models.Model):
    REPORT_CHOICES = [
        ('question', 'Question'),
        ('comment', 'Comment'),
        ('reply', 'Reply'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    report_type = models.CharField(max_length=10, choices=REPORT_CHOICES)
    report_id = models.PositiveIntegerField()
    reason = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Report by {self.user.username} on {self.report_type} {self.report_id}'
