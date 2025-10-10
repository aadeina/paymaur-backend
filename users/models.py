import uuid
import re
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.utils import timezone
from django.core.exceptions import ValidationError
from .managers import CustomUserManager


# ------------------------------
# Helper: validate Mauritanian phone numbers
# ------------------------------
def validate_mauritanian_phone(value):
    """
    Valid Mauritanian phone number rules:
    - Must be 8 digits.
    - Must start with:
        2 → Chinguitel
        3 → Mattel
        4 → Mauritel
    """
    if not re.fullmatch(r"[234]\d{7}", value):
        raise ValidationError(
            "Invalid Mauritanian phone number. Must start with 2, 3, or 4 and contain 8 digits."
        )
    return value


# ------------------------------
# User Model
# ------------------------------
class User(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = [
        ("CUSTOMER", "Customer"),
        ("AGENT", "Agent"),
        ("MERCHANT", "Merchant"),
        ("ADMIN", "Admin"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # core identity
    username = models.CharField(
        max_length=30,
        unique=True,
        help_text="Unique username used to identify the user within the app."
    )
    phone = models.CharField(
        max_length=8,
        unique=True,
        validators=[validate_mauritanian_phone],
        help_text="8-digit Mauritanian phone number (e.g., 36600100)"
    )

    # 4-digit PIN (Argon2-hashed via AbstractBaseUser.password field)
    # Example: input PIN '1234' → hashed automatically
    # Never store raw PINs.

    # roles & status
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="CUSTOMER")
    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)

    USERNAME_FIELD = "phone"
    REQUIRED_FIELDS = ["username"]

    objects = CustomUserManager()

    def __str__(self):
        return f"{self.username} ({self.phone})"

    class Meta:
        ordering = ["-date_joined"]
        verbose_name = "User"
        verbose_name_plural = "Users"
