from django.utils import timezone
from .models import Notification

def send_notification(user, title, message, channel="INAPP", metadata=None):
    """
    Create and optionally send a notification to a user.
    """

    notification = Notification.objects.create(
        user=user,
        title=title,
        message=message,
        channel=channel,
        metadata=metadata or {},
    )

    try:
        # Mock sending logic
        if channel == "SMS":
            # call your SMS API like Chinguisoft here
            print(f"[SMS] → {user.phone}: {message}")

        elif channel == "EMAIL":
            # call email provider API
            print(f"[EMAIL] → {user.username}: {title} - {message}")

        elif channel == "PUSH":
            # call push notification service
            print(f"[PUSH] → {user.username}: {message}")

        # If successful
        notification.status = "SENT"
        notification.sent_at = timezone.now()
        notification.save()

    except Exception as e:
        notification.status = "FAILED"
        notification.metadata["error"] = str(e)
        notification.save()

    return notification
