import uuid
from django.db import models
from django.utils import timezone

class Transaction(models.Model):
    TYPE_CHOICES = [
        ("TOPUP", "Top-up"),
        ("TRANSFER", "Transfer"),
        ("WITHDRAW", "Withdraw"),
        ("BILLPAY", "Bill Payment"),
    ]

    STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("SUCCESS", "Success"),
        ("FAILED", "Failed"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    wallet = models.ForeignKey("wallet.Wallet", on_delete=models.CASCADE, related_name="transactions")
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    balance_after = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="PENDING")
    reference = models.CharField(max_length=64, unique=True)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.type} | {self.amount} MRU | {self.status}"

    class Meta:
        ordering = ["-created_at"]
