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
    image = models.ImageField(upload_to="discussion_threads/",null = True,blank=True)
    def __str__(self):
        return self.thread_title

    class Meta:
        ordering = ['-updated']

    @property
    def likes_count(self):
        return self.reactions.filter(reaction_type='like').count()

    @property
    def loves_count(self):
        return self.reactions.filter(reaction_type='love').count()
    
    @property
    def haha_count(self):
        return self.reactions.filter(reaction_type='haha').count()

    @property
    def wow_count(self):
        return self.reactions.filter(reaction_type='wow').count()
    
    @property
    def sad_count(self):
        return self.reactions.filter(reaction_type='sad').count()

    @property
    def angry_count(self):
        return self.reactions.filter(reaction_type='angry').count()
    
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
    def reaction_icons():
        return {
            'like': '👍',
            'love': '❤️',
            'haha': '😂',
            'wow': '😮',
            'sad': '😢',
            'angry': '😡',
        }

    @staticmethod
    def reaction_labels():
        return {
            'like': 'Like',
            'love': 'Love',
            'haha': 'Haha',
            'wow': 'Wow',
            'sad': 'Sad',
            'angry': 'Angry',
        }

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
    reaction_type= models.CharField(max_length=10, choices=REACTION_CHOICES)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'comment')

    def __str__(self):
        return f"{self.user.username} reacted to {self.comment.comment_text[:20]} with {self.get_reaction_type_display()}"


class ReportThread(models.Model):
    REASON_CHOICES = [
        ('spam','Spam'),
        ('abuse','Abuse or harassment'),
        ('inappropriate','Inappropriate content'),
        ('other','Other'),
    ]
    thread = models.ForeignKey(DiscussionThread,on_delete=models.CASCADE)
    reported_by = models.ForeignKey(User,on_delete=models.CASCADE)
    reason = models.CharField(max_length=20,choices= REASON_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    additional_comments = models.TextField(blank=True, null=True) 
    def __str__(self):
        return f"Report for {self.thread.thread_title} by {self.reported_by.username}"
    
    
