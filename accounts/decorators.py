from django.http import HttpResponseForbidden
from functools import wraps

def role_required(allowed_roles):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped(request, *args, **kwargs):
            if not request.user.is_authenticated or request.user.role not in allowed_roles:
                return HttpResponseForbidden("You don't have permission to access this.")
            return view_func(request, *args, **kwargs)
        return _wrapped
    return decorator
