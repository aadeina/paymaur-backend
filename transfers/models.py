import uuid
from django.db import models, transaction
from django.utils import timezone

class Transfer(models.Model):
    STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("SUCCESS", "Success"),
        ("FAILED", "Failed"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sender_wallet = models.ForeignKey("wallet.Wallet", on_delete=models.CASCADE, related_name="sent_transfers")
    receiver_wallet = models.ForeignKey("wallet.Wallet", on_delete=models.CASCADE, related_name="received_transfers")
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    note = models.CharField(max_length=255, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="PENDING")
    reference = models.CharField(max_length=64, unique=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.sender_wallet.user.username} → {self.receiver_wallet.user.username} | {self.amount} MRU | {self.status}"

    class Meta:
        ordering = ["-created_at"]
