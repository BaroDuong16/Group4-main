from django.db import models
from django.utils import timezone
from course.models import Course
from user.models import User


class DiscussionThread(models.Model):
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    thread_title = models.CharField(max_length=255)
    thread_content = models.TextField(blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, null=True, blank=True)
    likes_count = models.PositiveIntegerField(default=0) 
    loves_count = models.PositiveIntegerField(default=0)
    image = models.ImageField(upload_to="discussion_threads/",null = True,blank=True)
    def save(self, *args, **kwargs):
        self.updated_at = timezone.now()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.thread_title

    class Meta:
        ordering = ['-updated']


class ThreadComments(models.Model):
    comment_id = models.AutoField(primary_key=True)
    thread = models.ForeignKey(DiscussionThread, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    comment_text = models.TextField()
    image = models.ImageField(upload_to = 'comment_threads/',null = True,blank = True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Comment by {self.user.username} on {self.thread.thread_title}"

    class Meta:
        ordering = ['-created']


# Reaction model for Threads
class ThreadReaction(models.Model):
    LIKE = 'like'
    LOVE = 'love'
    HAHA = 'haha'
    WOW = 'wow'
    SAD = 'sad'
    ANGRY = 'angry'

    REACTION_CHOICES = [
        (LIKE, 'Like'),
        (LOVE, 'Love'),
        (HAHA, 'Haha'),
        (WOW, 'Wow'),
        (SAD, 'Sad'),
        (ANGRY, 'Angry'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    thread = models.ForeignKey(DiscussionThread, on_delete=models.CASCADE, related_name='reactions')
    reaction_type = models.CharField(max_length=10, choices=REACTION_CHOICES)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'thread')

    def __str__(self):
        return f"{self.user.username} reacted to {self.thread.thread_title} with {self.get_reaction_type_display()}"


# Reaction model for Comments
class CommentReaction(models.Model):
    LIKE = 'like'
    LOVE = 'love'
    HAHA = 'haha'
    WOW = 'wow'
    SAD = 'sad'
    ANGRY = 'angry'

    REACTION_CHOICES = [
        (LIKE, 'Like'),
        (LOVE, 'Love'),
        (HAHA, 'Haha'),
        (WOW, 'Wow'),
        (SAD, 'Sad'),
        (ANGRY, 'Angry'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.ForeignKey(ThreadComments, on_delete=models.CASCADE, related_name='reactions')
    reaction_type = models.CharField(max_length=10, choices=REACTION_CHOICES)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'comment')

    def __str__(self):
        return f"{self.user.username} reacted to {self.comment.comment_text[:20]} with {self.get_reaction_type_display()}"
