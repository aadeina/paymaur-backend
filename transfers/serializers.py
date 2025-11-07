"""
Transfer Serializers
"""
from rest_framework import serializers
from decimal import Decimal
from django.db import transaction as db_transaction
import uuid

from .models import Transfer
from wallet.models import Wallet
from transactions.models import Transaction
from users.models import User


class TransferSerializer(serializers.ModelSerializer):
    """
    Transfer money between wallets
    """
    sender = serializers.CharField(source='sender_wallet.user.username', read_only=True)
    receiver = serializers.CharField(source='receiver_wallet.user.username', read_only=True)

    class Meta:
        model = Transfer
        fields = ['id', 'sender', 'receiver', 'amount', 'note', 'status', 'reference', 'created_at']
        read_only_fields = ['id', 'status', 'reference', 'created_at']


class CreateTransferSerializer(serializers.Serializer):
    """
    Serializer for creating a new transfer
    Supports lookup by username or phone
    """
    receiver_phone = serializers.CharField(
        max_length=8,
        required=False,
        help_text="Receiver's phone number"
    )
    receiver_username = serializers.CharField(
        max_length=30,
        required=False,
        help_text="Receiver's username"
    )
    amount = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        min_value=Decimal('1.00'),
        help_text="Amount to transfer (minimum 1 MRU)"
    )
    note = serializers.CharField(
        max_length=255,
        required=False,
        allow_blank=True,
        help_text="Optional transfer note"
    )

    def validate(self, data):
        """
        Ensure at least one receiver identifier is provided
        """
        if not data.get('receiver_phone') and not data.get('receiver_username'):
            raise serializers.ValidationError(
                "Either receiver_phone or receiver_username must be provided"
            )
        return data

    def create(self, validated_data):
        """
        Execute transfer with atomic database transaction
        """
        sender_wallet = self.context['request'].user.wallet
        amount = validated_data['amount']
        note = validated_data.get('note', '')

        # Find receiver
        receiver_user = None
        if validated_data.get('receiver_phone'):
            try:
                receiver_user = User.objects.get(phone=validated_data['receiver_phone'])
            except User.DoesNotExist:
                raise serializers.ValidationError({"receiver_phone": "User not found with this phone number"})
        elif validated_data.get('receiver_username'):
            try:
                receiver_user = User.objects.get(username=validated_data['receiver_username'])
            except User.DoesNotExist:
                raise serializers.ValidationError({"receiver_username": "User not found with this username"})

        receiver_wallet = receiver_user.wallet

        # Validation
        if sender_wallet.id == receiver_wallet.id:
            raise serializers.ValidationError("Cannot transfer to yourself")

        if sender_wallet.is_locked:
            raise serializers.ValidationError("Your wallet is locked")

        if receiver_wallet.is_locked:
            raise serializers.ValidationError("Receiver's wallet is locked")

        if sender_wallet.balance < amount:
            raise serializers.ValidationError(
                f"Insufficient balance. Available: {sender_wallet.balance} MRU"
            )

        # Execute transfer atomically
        with db_transaction.atomic():
            # Generate unique reference for the transfer
            transfer_reference = f"TRF-{uuid.uuid4().hex[:12].upper()}"

            # Debit sender
            sender_wallet.balance -= amount
            sender_wallet.save()

            # Credit receiver
            receiver_wallet.balance += amount
            receiver_wallet.save()

            # Create transfer record
            transfer = Transfer.objects.create(
                sender_wallet=sender_wallet,
                receiver_wallet=receiver_wallet,
                amount=amount,
                note=note,
                status="SUCCESS",
                reference=transfer_reference
            )

            # Create transaction records for both parties with unique references
            Transaction.objects.create(
                wallet=sender_wallet,
                type="TRANSFER",
                amount=-amount,  # Negative for debit
                balance_after=sender_wallet.balance,
                status="SUCCESS",
                reference=f"{transfer_reference}-OUT",  # Unique reference for sender
                metadata={
                    "transfer_id": str(transfer.id),
                    "transfer_reference": transfer_reference,
                    "receiver": receiver_user.username,
                    "note": note
                }
            )

            Transaction.objects.create(
                wallet=receiver_wallet,
                type="TRANSFER",
                amount=amount,  # Positive for credit
                balance_after=receiver_wallet.balance,
                status="SUCCESS",
                reference=f"{transfer_reference}-IN",  # Unique reference for receiver
                metadata={
                    "transfer_id": str(transfer.id),
                    "transfer_reference": transfer_reference,
                    "sender": self.context['request'].user.username,
                    "note": note
                }
            )

        return transfer
