import uuid
from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator


class BillPayment(models.Model):
    CATEGORY_CHOICES = [
        ("ELECTRICITY", "Electricity"),
        ("WATER", "Water"),
        ("INTERNET", "Internet"),
        ("TV", "Television"),
        ("OTHER", "Other"),
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
        related_name="bills",
        help_text="The wallet from which this bill is paid."
    )

    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    provider_name = models.CharField(max_length=100, help_text="Bill provider name, e.g., SOMELEC, Mauritel.")
    account_number = models.CharField(max_length=30, help_text="User’s account ID at the provider.")
    customer_name = models.CharField(max_length=100, help_text="Name of the bill owner or subscriber.")

    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(1)],
        help_text="Bill amount in MRU."
    )

    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="PENDING")

    reference = models.CharField(max_length=64, unique=True, help_text="Unique payment reference.")
    idempotency_key = models.CharField(max_length=64, unique=True, help_text="Prevents double payment processing.")
    metadata = models.JSONField(default=dict, blank=True)

    created_at = models.DateTimeField(default=timezone.now)
    completed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.provider_name} | {self.account_number} | {self.amount} MRU | {self.status}"

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Bill Payment"
        verbose_name_plural = "Bill Payments"
