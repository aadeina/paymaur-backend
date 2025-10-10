import uuid
from django.db import models
from django.utils import timezone


class PopulationRecord(models.Model):
    nni = models.CharField(max_length=30, primary_key=True)
    full_name = models.CharField(max_length=255)
    dob = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.full_name} ({self.nni})"


class SimpleKYC(models.Model):
    STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("VERIFIED", "Verified"),
        ("REJECTED", "Rejected"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField("users.User", on_delete=models.CASCADE, related_name="simple_kyc")
    nni = models.CharField(max_length=30, unique=True)
    full_name = models.CharField(max_length=255)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="PENDING")
    source = models.CharField(max_length=20, default="SIMULATED")
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    verified_at = models.DateTimeField(null=True, blank=True)
    verified_by = models.ForeignKey("users.User", null=True, blank=True, on_delete=models.SET_NULL, related_name="kyc_verified")

    def __str__(self):
        return f"{self.user.username} - {self.nni} ({self.status})"
