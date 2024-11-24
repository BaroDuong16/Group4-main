#add this into Middleware in settings.py (Ex:MIDDLEWARE = [
#    'django.middleware.security.SecurityMiddleware',
#    'django.contrib.sessions.middleware.SessionMiddleware',
#    'django.middleware.common.CommonMiddleware',
#    'django.middleware.csrf.CsrfViewMiddleware',
#   'django.contrib.auth.middleware.AuthenticationMiddleware',
#    'django.contrib.messages.middleware.MessageMiddleware',
#    'django.middleware.clickjacking.XFrameOptionsMiddleware',
#    'activity.activity_tracking_middleware.ActivityTrackingMiddleware',        add like this 
#])

from django.utils import timezone
from django.urls import resolve
from .models import UserActivityLog

class ActivityTrackingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Process the request
        response = self.get_response(request)

        # Log activity if the user is authenticated
        if request.user.is_authenticated:
            current_url = resolve(request.path_info).url_name
            
            # Check if the user has already accessed the activity page
            if current_url == 'activity_view':  # Replace with the actual URL name for activity view
                if not request.session.get('activity_page_accessed', False):
                    # Log the activity
                    UserActivityLog.objects.create(
                        user=request.user,
                        activity_type='page_visit',
                        activity_details=f"Accessed {current_url}",
                        activity_timestamp=timezone.now()
                    )
                    # Set the flag in the session to True
                    request.session['activity_page_accessed'] = True
            else:
                # Reset the flag if they navigate away from the activity page
                request.session['activity_page_accessed'] = False

        return response