from django.contrib.auth.models import BaseUserManager


class CustomUserManager(BaseUserManager):
    def create_user(self, phone, username, password=None, **extra_fields):
        if not phone:
            raise ValueError("Phone number is required")
        if not username:
            raise ValueError("Username is required")

        user = self.model(phone=phone, username=username, **extra_fields)
        user.set_password(password)  # hashes PIN with Argon2
        user.save(using=self._db)
        return user

    def create_superuser(self, phone, username, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("role", "ADMIN")

        return self.create_user(phone, username, password, **extra_fields)
