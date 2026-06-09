from .context import current_user, current_request
from .models import UserActivity


def get_device_type(user_agent):
    ua = user_agent.lower()
    if "mobile" in ua:
        return "mobile"
    elif "tablet" in ua:
        return "tablet"
    return "desktop"


def build_metadata(extra=None):
    request = current_request.get()
    user = current_user.get()
    metadata = {}

    if request:
        ua = request.META.get("HTTP_USER_AGENT", "")
        metadata.update({
            "ip": request.META.get("REMOTE_ADDR"),
            "user_agent": ua,
            "device_type": get_device_type(ua),
            "method": request.method,
            "path": request.path,
        })

    if user:
        metadata["role"] = getattr(user, "role", None)

    if extra:
        metadata.update(extra)

    return metadata


def log_activity(event_type, action_type, entity_name=None, entity_id=None, extra_metadata=None):
    user = current_user.get()
    try:
        UserActivity.objects.create(
            user_id=user.id if user else None,
            event_type=event_type,
            action_type=action_type,
            entity_name=entity_name,
            metadata=build_metadata(extra=extra_metadata),
        )
    except Exception as e:
        print(f"Activity log failed: {e}")