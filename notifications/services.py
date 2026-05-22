from .models import Notification
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer


def create_notification(user, title, message):

    notification = Notification.objects.create(
        user=user,
        title=title,
        message=message
    )

    print("GROUP SEND RUNNING")

    channel_layer = get_channel_layer()

    print(channel_layer)

    print(f"Sending to group: user_{user.id}")

    async_to_sync(channel_layer.group_send)(
        f"user_{user.id}",
        {
            "type": "send_notification",
            "data": {
                "title": title,
                "message": message,
            }
        }
    )

    return notification
