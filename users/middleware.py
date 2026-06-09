import time
from activity.models import UserActivity

print("MIDDLEWARE FILE LOADED")

class UserActivityMiddleware:
    def __init__(self, get_response):
        print("MIDDLEWARE INIT") 
        self.get_response = get_response

    def __call__(self, request):
        start_time = time.time()
        response = self.get_response(request)
        end_time = time.time()

        excluded_paths = [
            "/admin/jsi18n/",
            "/favicon.ico",
            "/static/",
            "/media/",
            "/admin/"
        ]

        if any(request.path.startswith(path) for path in excluded_paths):
            return response

        user = request.user if request.user.is_authenticated else None

        metadata = {
            "ip": request.META.get("REMOTE_ADDR"),
            "user_agent": request.META.get("HTTP_USER_AGENT", ""),
            "method": request.method,
            "status_code": response.status_code,
            "response_time_ms": round((end_time - start_time) * 1000, 2),
        }

        if user:
            metadata["role"] = getattr(user, "role", None)

        try:
            UserActivity.objects.create(
                user_id=user.id if user else None,
                event_type="BROWSE",
                action_type="VISIT",
                entity_name=request.path,
                metadata=metadata,
            )
            print("Activity logged: " + request.path)
        except Exception as e:
            print("Activity log failed: " + str(e))

        return response