from django.conf import settings
from django.shortcuts import redirect
from django.utils.deprecation import MiddlewareMixin


class LoginRequiredMiddleware(MiddlewareMixin):
    """
    Enforce authentication on all views except a small whitelist
    (login/logout/password reset, admin and static/media).
    Uses settings.LOGIN_URL for redirects and preserves the "next" param.
    """

    EXEMPT_PREFIXES = (
        "/accounts/",  # django.contrib.auth URLs (login/logout/password reset)
        "/admin/",
        "/static/",
        "/media/",
        "/favicon.ico",
    )

    def process_request(self, request):
        # Already authenticated? Allow.
        user = getattr(request, "user", None)
        if user and user.is_authenticated:
            return None

        path = request.path

        # Allow whitelisted paths.
        for prefix in self.EXEMPT_PREFIXES:
            if path.startswith(prefix):
                return None

        # Redirect to login with next parameter
        login_url = getattr(settings, "LOGIN_URL", "/accounts/login/")
        return redirect(f"{login_url}?next={path}")
