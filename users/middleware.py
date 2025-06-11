from datetime import timedelta

from django.utils.timezone import now


class UpdateLastActivityMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if request.user.is_authenticated:
            last_activity = request.user.last_activity
            if not last_activity or now() - last_activity > timedelta(seconds=30):
                request.user.last_activity = now()
                request.user.save(update_fields=["last_activity"])
        return response
