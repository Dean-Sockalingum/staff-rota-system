from django.http import JsonResponse
from django.conf import settings
from django.contrib.auth.decorators import user_passes_test


def _is_staff(user):
    return bool(user and user.is_authenticated and user.is_staff)


@user_passes_test(_is_staff)
def health_config(request):
    """Return runtime config values for operational verification.
    Staff-only endpoint exposing hosts/origins and debug flag.
    """
    data = {
        'DEBUG': bool(settings.DEBUG),
        'ALLOWED_HOSTS': list(settings.ALLOWED_HOSTS or []),
        'CSRF_TRUSTED_ORIGINS': list(settings.CSRF_TRUSTED_ORIGINS or []),
    }
    return JsonResponse(data)
