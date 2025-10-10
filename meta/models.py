import uuid
from django.db import models
from django.utils import timezone

class Operator(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=50, unique=True)
    code = models.CharField(max_length=10, unique=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.name


class Biller(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=50)  # Electricity, Water, Internet...
    operator = models.ForeignKey(
        Operator, on_delete=models.SET_NULL, null=True, blank=True
    )
    api_endpoint = models.URLField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} ({self.category})"


class Currency(models.Model):
    code = models.CharField(max_length=3, unique=True)  # MRU, USD, EUR
    symbol = models.CharField(max_length=5, default="UM")
    name = models.CharField(max_length=50)
    is_default = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.code} ({self.symbol})"
