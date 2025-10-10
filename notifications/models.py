import uuid
from django.db import models
from django.utils import timezone

class Notification(models.Model):
    CHANNEL_CHOICES = [
        ("SMS", "SMS"),
        ("EMAIL", "Email"),
        ("PUSH", "Push"),
        ("INAPP", "In-App"),
    ]

    STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("SENT", "Sent"),
        ("FAILED", "Failed"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        related_name="notifications"
    )
    title = models.CharField(max_length=150)
    message = models.TextField()
    channel = models.CharField(max_length=10, choices=CHANNEL_CHOICES, default="INAPP")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="PENDING")
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    sent_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} | {self.title} | {self.status}"

    class Meta:
        ordering = ["-created_at"]
