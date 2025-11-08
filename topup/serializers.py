"""
Top-up Serializers
Mobile recharge for Mauritanian operators
"""
from rest_framework import serializers
from decimal import Decimal
from django.db import transaction as db_transaction
import uuid

from .models import Topup
from transactions.models import Transaction
from users.models import validate_mauritanian_phone


class TopupSerializer(serializers.ModelSerializer):
    """
    Top-up information serializer
    """
    wallet_owner = serializers.CharField(source='wallet.user.username', read_only=True)

    class Meta:
        model = Topup
        fields = ['id', 'wallet_owner', 'operator', 'phone_number', 'amount', 'status', 'reference', 'idempotency_key', 'metadata', 'created_at', 'completed_at']
        read_only_fields = ['id', 'wallet_owner', 'status', 'reference', 'idempotency_key', 'created_at', 'completed_at']


class CreateTopupSerializer(serializers.Serializer):
    """
    Create a new mobile top-up
    """
    operator = serializers.ChoiceField(
        choices=['MATTEL', 'CHINGUITEL', 'MAURITEL'],
        help_text="Mobile operator (MATTEL, CHINGUITEL, MAURITEL)"
    )
    phone_number = serializers.CharField(
        max_length=8,
        min_length=8,
        help_text="8-digit Mauritanian phone number to recharge"
    )
    amount = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        min_value=Decimal('10.00'),
        max_value=Decimal('10000.00'),
        help_text="Amount to recharge (10-10000 MRU)"
    )

    def validate_phone_number(self, value):
        """Validate Mauritanian phone format"""
        validate_mauritanian_phone(value)
        return value

    def validate(self, data):
        """Validate operator and phone number match"""
        phone = data.get('phone_number')
        operator = data.get('operator')

        # Check if phone prefix matches operator
        operator_prefixes = {
            'MATTEL': '3',
            'CHINGUITEL': '2',
            'MAURITEL': '4'
        }

        expected_prefix = operator_prefixes.get(operator)
        if phone and not phone.startswith(expected_prefix):
            raise serializers.ValidationError({
                'phone_number': f'{operator} numbers must start with {expected_prefix}'
            })

        return data

    def create(self, validated_data):
        """
        Execute top-up with wallet deduction and transaction recording
        """
        user = self.context['request'].user
        wallet = user.wallet

        operator = validated_data['operator']
        phone_number = validated_data['phone_number']
        amount = validated_data['amount']

        # Validation
        if wallet.is_locked:
            raise serializers.ValidationError("Your wallet is locked")

        if wallet.balance < amount:
            raise serializers.ValidationError(
                f"Insufficient balance. Available: {wallet.balance} MRU, Required: {amount} MRU"
            )

        # Execute top-up atomically
        with db_transaction.atomic():
            # Generate unique references
            reference = f"TOP-{uuid.uuid4().hex[:12].upper()}"
            idempotency_key = f"{user.id}-{phone_number}-{amount}-{uuid.uuid4().hex[:8]}"

            # Deduct from wallet
            wallet.balance -= amount
            wallet.save()

            # Create top-up record
            topup = Topup.objects.create(
                wallet=wallet,
                operator=operator,
                phone_number=phone_number,
                amount=amount,
                status="SUCCESS",  # In production, this would be PENDING until operator confirms
                reference=reference,
                idempotency_key=idempotency_key,
                metadata={
                    'user': user.username,
                    'user_phone': user.phone
                }
            )

            # Create transaction record
            Transaction.objects.create(
                wallet=wallet,
                type="TOPUP",
                amount=-amount,  # Negative for debit
                balance_after=wallet.balance,
                status="SUCCESS",
                reference=reference,
                metadata={
                    'topup_id': str(topup.id),
                    'operator': operator,
                    'phone_number': phone_number,
                    'type': 'mobile_recharge'
                }
            )

            # Mark as completed (in production, wait for operator webhook)
            from django.utils import timezone
            topup.completed_at = timezone.now()
            topup.save()

        return topup
