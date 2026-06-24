import time
from activity.models import UserActivity
from activity.context import current_user, current_request
from activity.utils import log_activity

print("MIDDLEWARE FILE LOADED")

class UserActivityMiddleware:
    def __init__(self, get_response):
        print("MIDDLEWARE INIT") 
        self.get_response = get_response

    def __call__(self, request):
        start_time = time.time()
        user = request.user if request.user.is_authenticated else None
        user_token = current_user.set(user)
        request_token = current_request.set(request)
        response = self.get_response(request)
        end_time = time.time()

        included_paths = [
            # "/jobs/",
        ]

        if not any(request.path.startswith(path) for path in included_paths):
            return response
        try : 
            log_activity(
                event_type="browse",
                action_type="visit",
                entity_name=request.path,
                extra_metadata={
                    "status_code": response.status_code,
                    "response_time_ms": round((end_time - start_time) * 1000, 2),
                }
            )
        except Exception as e : 
            pass
        finally :
            current_user.reset(user_token)
            current_request.reset(request_token)
        return response
    