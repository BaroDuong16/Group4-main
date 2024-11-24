# from django.db import models
# from user.models import User

# app_name = 'chat'

# class Chat(models.Model):
#     sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
#     receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
#     message = models.TextField()
#     timestamp = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return f'{self.sender.username} -> {self.receiver.username}: {self.message[:20]}'

from django.db import models
from user.models import User

class GroupChat(models.Model):
    name = models.CharField(max_length=100)  # Name of the group chat
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_groups')
    members = models.ManyToManyField(User, related_name='group_members')  # Group members
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Group: {self.name}'

class Chat(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages', null=True, blank=True)
    group = models.ForeignKey(GroupChat, on_delete=models.CASCADE, related_name='group_messages', null=True, blank=True)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    edited_at = models.DateTimeField(null=True, blank=True)
    is_read = models.BooleanField(default=False)  # Track if the message has been read

    def __str__(self):
        if self.group:
            return f'{self.sender.username} -> Group {self.group.name}: {self.message[:20]}'
        return f'{self.sender.username} -> {self.receiver.username}: {self.message[:20]}'
