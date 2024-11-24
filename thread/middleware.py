from typing import Any
from transformers import pipeline
from django.conf import settings
from django.shortcuts import redirect

class AIModerationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.moderation_pipeline = pipeline("text-classification", model="unitary/toxic-bert")

    def __call__(self, request):
        if request.method == 'POST' and 'comment_text' in request.POST:
            comment_text = request.POST['comment_text']
            if not self.is_content_appropriate(comment_text):
                return redirect('thread:moderation_warning')
        response = self.get_response(request)
        return response

    def is_content_appropriate(self, text):
        results = self.moderation_pipeline(text)
        for result in results:
            if result['label'] == 'toxic' and result['score'] > 0.5:
                return False
        return True