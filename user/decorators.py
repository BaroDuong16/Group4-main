from django.shortcuts import redirect
from django.contrib import messages
from functools import wraps

def role_required(required_roles):
    """
    Decorator to check if the user has the specified role(s) or is a superuser.
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if request.user.is_authenticated:
                if request.user.is_superuser:
                    return view_func(request, *args, **kwargs)

                user_role = request.user.profile.role.role_name.lower()
                if user_role in [role.lower() for role in required_roles]:
                    return view_func(request, *args, **kwargs)
                else:
                    messages.error(request, "You do not have permission to access this page.")
                    return redirect('user:user_list')  
            else:
                return redirect('login')

        return _wrapped_view
    return decorator