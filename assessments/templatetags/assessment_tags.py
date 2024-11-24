
from django import template

register = template.Library()

@register.filter
def get_item(attempts, user_id):
    """Get the attempt related to a specific user ID."""
    print(f"attempts: {attempts}, user_id: {user_id}")  # Debugging line
    return attempts.filter(user_id=user_id).first()
