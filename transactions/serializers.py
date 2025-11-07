"""
Transaction Serializers
"""
from rest_framework import serializers
from .models import Transaction


class TransactionSerializer(serializers.ModelSerializer):
    """
    Transaction history serializer
    """
    wallet_owner = serializers.CharField(source='wallet.user.username', read_only=True)

    class Meta:
        model = Transaction
        fields = ['id', 'wallet_owner', 'type', 'amount', 'balance_after', 'status', 'reference', 'metadata', 'created_at']
        read_only_fields = fields
