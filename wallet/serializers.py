"""
Wallet Serializers
"""
from rest_framework import serializers
from .models import Wallet


class WalletSerializer(serializers.ModelSerializer):
    """
    Wallet information serializer
    """
    username = serializers.CharField(source='user.username', read_only=True)
    phone = serializers.CharField(source='user.phone', read_only=True)

    class Meta:
        model = Wallet
        fields = ['id', 'username', 'phone', 'balance', 'is_locked', 'last_updated']
        read_only_fields = ['id', 'balance', 'last_updated']
