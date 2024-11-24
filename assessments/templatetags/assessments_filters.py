from django import template

register = template.Library()

@register.filter
def get_attempt_by_candidate(attempts, email):
    for attempt in attempts:
        if attempt.user.email == email:
            return attempt
    return None
