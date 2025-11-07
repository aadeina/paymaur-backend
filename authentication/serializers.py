# authentication/serializers.py

from django.contrib.auth.hashers import make_password, check_password
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from users.models import User
from .models import OTP


# -----------------------------
# ✅ Register Serializer
# -----------------------------
class RegisterSerializer(serializers.ModelSerializer):
    pin = serializers.CharField(write_only=True, min_length=4, max_length=4)

    class Meta:
        model = User
        fields = ["phone", "username", "pin"]

    def create(self, validated_data):
        """
        Convert raw PIN into Argon2-hashed password (never store raw PIN).
        """
        validated_data["password"] = make_password(validated_data.pop("pin"))
        return User.objects.create(**validated_data)


# -----------------------------
# ✅ Login Serializer
# -----------------------------
class LoginSerializer(serializers.Serializer):
    phone = serializers.CharField()
    pin = serializers.CharField(write_only=True)


# -----------------------------
# ✅ OTP Verification Serializer
# -----------------------------
class OTPVerifySerializer(serializers.Serializer):
    phone = serializers.CharField()
    code = serializers.CharField()
    purpose = serializers.ChoiceField(choices=["REGISTER", "RESET_PIN"])


# -----------------------------
# ✅ Logout Serializer
# -----------------------------
class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()

    def validate(self, attrs):
        self.token = attrs["refresh"]
        return attrs

    def save(self, **kwargs):
        """
        Blacklist the refresh token to prevent reuse.
        """
        try:
            token = RefreshToken(self.token)
            token.blacklist()
        except Exception:
            raise serializers.ValidationError("Invalid or expired token.")


# -----------------------------
# ✅ Change PIN Serializer
# -----------------------------
class ChangePINSerializer(serializers.Serializer):
    old_pin = serializers.CharField(min_length=4, max_length=4)
    new_pin = serializers.CharField(min_length=4, max_length=4)

    def validate(self, attrs):
        user = self.context["request"].user
        if not check_password(attrs["old_pin"], user.password):
            raise serializers.ValidationError("Old PIN is incorrect.")
        return attrs

    def save(self, **kwargs):
        """
        Update the user’s PIN securely using Argon2 hashing.
        """
        user = self.context["request"].user
        user.set_password(self.validated_data["new_pin"])
        user.save()
        return user


# -----------------------------
# ✅ Reset PIN Serializer
# -----------------------------
class ResetPINSerializer(serializers.Serializer):
    phone = serializers.CharField()
    new_pin = serializers.CharField(min_length=4, max_length=4)

    def save(self, **kwargs):
        """
        Reset user PIN securely after OTP verification.
        """
        phone = self.validated_data["phone"]
        user = User.objects.filter(phone=phone).first()
        if not user:
            raise serializers.ValidationError("User not found.")

        user.set_password(self.validated_data["new_pin"])
        user.save()
        return user
