from .context import current_user, current_request
from .models import UserActivity
from .logger import activity_logger

import json
import threading

from django.utils import timezone

_buffer = []
_buffer_lock = threading.Lock()
DB_LOGGING_ENABLED = True

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
    
    print(f"log_activity called: entity_id={entity_id}") 
    user = current_user.get()
    print("current user is " ,user)
    metadata = build_metadata(extra=extra_metadata)
    entry = {
        "user_id": user.id if user else None,
        "event_type": event_type,
        "action_type": action_type,
        "entity_name": entity_name,
        "entity_id" : entity_id,
        "metadata": metadata,
        "created_at": timezone.now(),
    }
    activity_logger.info(json.dumps(entry, default=str))
    if DB_LOGGING_ENABLED:
        with _buffer_lock:
            _buffer.append(entry)


def flush_to_db():

    if not DB_LOGGING_ENABLED:
        return

    with _buffer_lock:
        if not _buffer:
            return
        to_insert = _buffer.copy()
        _buffer.clear()

    try:
        UserActivity.objects.bulk_create([
            UserActivity(
                user_id=e["user_id"],
                event_type=e["event_type"],
                action_type=e["action_type"],
                entity_name=e["entity_name"],
                metadata=e["metadata"],
                created_at=e["created_at"],
            )
            for e in to_insert
        ])
        print(f"[ACTIVITY] Flushed {len(to_insert)} records to DB")
    except Exception as ex:
        print(f"[ACTIVITY] DB flush failed: {ex}")
