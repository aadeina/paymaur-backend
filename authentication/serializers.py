"""
Authentication Serializers
Handles user registration, login, and token management
"""
from rest_framework import serializers
from django.contrib.auth import authenticate
from users.models import User
from wallet.models import Wallet


class RegisterSerializer(serializers.ModelSerializer):
    """
    User registration serializer
    Creates new user with phone, username, and 4-digit PIN
    """
    password = serializers.CharField(
        write_only=True,
        min_length=4,
        max_length=4,
        style={'input_type': 'password'},
        help_text="4-digit PIN"
    )
    password_confirm = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'},
        help_text="Confirm 4-digit PIN"
    )

    class Meta:
        model = User
        fields = ['phone', 'username', 'password', 'password_confirm', 'role']
        extra_kwargs = {
            'role': {'default': 'CUSTOMER', 'required': False}
        }

    def validate_phone(self, value):
        """Ensure phone number is 8 digits and starts with 2, 3, or 4"""
        if len(value) != 8:
            raise serializers.ValidationError("Phone number must be exactly 8 digits")
        if value[0] not in ['2', '3', '4']:
            raise serializers.ValidationError("Phone must start with 2, 3, or 4 (Mauritanian operators)")
        return value

    def validate_password(self, value):
        """Ensure PIN is exactly 4 digits"""
        if not value.isdigit():
            raise serializers.ValidationError("PIN must contain only digits")
        if len(value) != 4:
            raise serializers.ValidationError("PIN must be exactly 4 digits")
        return value

    def validate(self, data):
        """Ensure passwords match"""
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError({"password_confirm": "PINs do not match"})
        return data

    def create(self, validated_data):
        """Create user and automatically create their wallet"""
        validated_data.pop('password_confirm')

        user = User.objects.create_user(
            phone=validated_data['phone'],
            username=validated_data['username'],
            password=validated_data['password'],
            role=validated_data.get('role', 'CUSTOMER')
        )

        # Automatically create wallet for new user
        Wallet.objects.create(user=user)

        return user


class LoginSerializer(serializers.Serializer):
    """
    User login serializer
    Authenticates using phone + 4-digit PIN
    """
    phone = serializers.CharField(max_length=8)
    password = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'},
        help_text="4-digit PIN"
    )

    def validate(self, data):
        """Authenticate user with phone and PIN"""
        phone = data.get('phone')
        password = data.get('password')

        if not phone or not password:
            raise serializers.ValidationError("Must provide phone and PIN")

        user = authenticate(username=phone, password=password)

        if not user:
            raise serializers.ValidationError("Invalid credentials")

        if not user.is_active:
            raise serializers.ValidationError("User account is disabled")

        data['user'] = user
        return data


class UserSerializer(serializers.ModelSerializer):
    """
    Basic user information serializer
    Used in responses after registration/login
    """
    wallet_balance = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'phone', 'role', 'is_verified', 'is_active', 'date_joined', 'wallet_balance']
        read_only_fields = ['id', 'date_joined', 'is_verified']

    def get_wallet_balance(self, obj):
        """Include wallet balance in user info"""
        try:
            return str(obj.wallet.balance)
        except:
            return "0.00"
