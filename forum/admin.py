from django.contrib import admin
from .models import ForumQuestion, ForumComment, Reply

# Register your models here.
admin.site.register(ForumQuestion)
admin.site.register(ForumComment)
admin.site.register(Reply)