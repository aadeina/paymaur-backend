import uuid
from django.db import models
from django.utils import timezone

class FeeRule(models.Model):
    OPERATION_CHOICES = [
        ("TRANSFER", "Wallet Transfer"),
        ("TOPUP", "Mobile Top-up"),
        ("BILLPAY", "Bill Payment"),
        ("CASHIN", "Cash In"),
        ("CASHOUT", "Cash Out"),
        ("AGENT_COMMISSION", "Agent Commission"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    operation = models.CharField(max_length=30, choices=OPERATION_CHOICES, unique=True)
    rate_percent = models.DecimalField(
        max_digits=5,
        decimal_places=3,
        help_text="Percentage (e.g. 1.500 = 1.5%)"
    )
    fixed_fee = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text="Flat fee in MRU, added to the percentage fee."
    )
    min_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    max_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.operation}: {self.rate_percent}% + {self.fixed_fee} MRU"

    class Meta:
        verbose_name = "Fee Rule"
        verbose_name_plural = "Fee Rules"
        ordering = ["operation"]


class FeeTransaction(models.Model):
    """
    Stores every fee or commission applied in the system.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    wallet = models.ForeignKey(
        "wallet.Wallet",
        on_delete=models.CASCADE,
        related_name="fee_transactions"
    )
    rule = models.ForeignKey(
        FeeRule,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="transactions"
    )
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    reference = models.CharField(max_length=64, unique=True)
    created_at = models.DateTimeField(default=timezone.now)
    metadata = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return f"{self.amount} MRU fee | {self.rule.operation if self.rule else 'Custom'}"

    class Meta:
        verbose_name = "Fee Transaction"
        verbose_name_plural = "Fee Transactions"
        ordering = ["-created_at"]
