import uuid
from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator


class Topup(models.Model):
    OPERATOR_CHOICES = [
        ("MATTEL", "Mattel"),
        ("CHINGUITEL", "Chinguitel"),
        ("MAURITEL", "Mauritel"),
    ]

    STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("SUCCESS", "Success"),
        ("FAILED", "Failed"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    wallet = models.ForeignKey(
        "wallet.Wallet",
        on_delete=models.CASCADE,
        related_name="topups",
        help_text="The wallet from which this top-up is paid."
    )

    operator = models.CharField(max_length=20, choices=OPERATOR_CHOICES)
    phone_number = models.CharField(
        max_length=8,
        help_text="The 8-digit Mauritanian number to top up (2,3,4 prefixes)."
    )
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(1)]
    )
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default="PENDING"
    )

    reference = models.CharField(
        max_length=64,
        unique=True,
        help_text="Unique transaction reference for audit tracking."
    )
    idempotency_key = models.CharField(
        max_length=64,
        unique=True,
        help_text="Prevents double processing of the same top-up request."
    )

    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    completed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.operator} | {self.phone_number} | {self.amount} MRU | {self.status}"

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Top-up"
        verbose_name_plural = "Top-ups"
