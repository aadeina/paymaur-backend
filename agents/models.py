import uuid
from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator


# ----------------------------
# Agent Model
# ----------------------------
class Agent(models.Model):
    """
    Represents a registered PayMaur agent who can perform cash-in/cash-out operations.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        "users.User",
        on_delete=models.CASCADE,
        related_name="agent_profile",
        help_text="Linked user account for this agent."
    )
    name = models.CharField(max_length=100, help_text="Official agent name or kiosk name.")
    location = models.CharField(max_length=255, help_text="Physical address or area (e.g., Tevragh Zeina).")
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.name} ({'Active' if self.is_active else 'Inactive'})"

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Agent"
        verbose_name_plural = "Agents"


# ----------------------------
# AgentTransaction Model
# ----------------------------
class AgentTransaction(models.Model):
    """
    Records every cash-in / cash-out transaction processed through an agent.
    """

    TYPE_CHOICES = [
        ("CASHIN", "Cash In"),
        ("CASHOUT", "Cash Out"),
    ]

    STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("SUCCESS", "Success"),
        ("FAILED", "Failed"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    agent = models.ForeignKey(
        Agent,
        on_delete=models.CASCADE,
        related_name="transactions",
        help_text="The agent performing this operation."
    )
    wallet = models.ForeignKey(
        "wallet.Wallet",
        on_delete=models.CASCADE,
        related_name="agent_transactions",
        help_text="The wallet involved in this transaction."
    )
    type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(1)],
        help_text="Amount of money handled in MRU."
    )
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default="PENDING"
    )
    token = models.CharField(
        max_length=8,
        unique=True,
        help_text="Unique 8-digit verification code (used for cash-out)."
    )
    reference = models.CharField(
        max_length=64,
        unique=True,
        help_text="Unique transaction reference for audit tracking."
    )
    idempotency_key = models.CharField(
        max_length=64,
        unique=True,
        help_text="Prevents double processing of the same cash operation."
    )
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    completed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.type} | {self.amount} MRU | {self.status}"

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Agent Transaction"
        verbose_name_plural = "Agent Transactions"
