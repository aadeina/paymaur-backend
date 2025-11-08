"""
Bill Payment Serializers
Utility bill payments (electricity, water, internet, etc.)
"""
from rest_framework import serializers
from decimal import Decimal
from django.db import transaction as db_transaction
import uuid

from .models import BillPayment
from transactions.models import Transaction


class BillPaymentSerializer(serializers.ModelSerializer):
    """
    Bill payment information serializer
    """
    wallet_owner = serializers.CharField(source='wallet.user.username', read_only=True)

    class Meta:
        model = BillPayment
        fields = ['id', 'wallet_owner', 'category', 'provider_name', 'account_number', 'customer_name', 'amount', 'status', 'reference', 'idempotency_key', 'metadata', 'created_at', 'completed_at']
        read_only_fields = ['id', 'wallet_owner', 'status', 'reference', 'idempotency_key', 'created_at', 'completed_at']


class CreateBillPaymentSerializer(serializers.Serializer):
    """
    Create a new bill payment
    """
    category = serializers.ChoiceField(
        choices=['ELECTRICITY', 'WATER', 'INTERNET', 'TV', 'OTHER'],
        help_text="Bill category"
    )
    provider_name = serializers.CharField(
        max_length=100,
        help_text="Provider name (e.g., SOMELEC, SNDE, Mauritel)"
    )
    account_number = serializers.CharField(
        max_length=30,
        help_text="Your account number at the provider"
    )
    customer_name = serializers.CharField(
        max_length=100,
        help_text="Name on the account"
    )
    amount = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        min_value=Decimal('1.00'),
        max_value=Decimal('100000.00'),
        help_text="Bill amount (1-100000 MRU)"
    )

    def create(self, validated_data):
        """
        Execute bill payment with wallet deduction and transaction recording
        """
        user = self.context['request'].user
        wallet = user.wallet

        category = validated_data['category']
        provider_name = validated_data['provider_name']
        account_number = validated_data['account_number']
        customer_name = validated_data['customer_name']
        amount = validated_data['amount']

        # Validation
        if wallet.is_locked:
            raise serializers.ValidationError("Your wallet is locked")

        if wallet.balance < amount:
            raise serializers.ValidationError(
                f"Insufficient balance. Available: {wallet.balance} MRU, Required: {amount} MRU"
            )

        # Execute bill payment atomically
        with db_transaction.atomic():
            # Generate unique references
            reference = f"BILL-{uuid.uuid4().hex[:12].upper()}"
            idempotency_key = f"{user.id}-{account_number}-{amount}-{uuid.uuid4().hex[:8]}"

            # Deduct from wallet
            wallet.balance -= amount
            wallet.save()

            # Create bill payment record
            bill_payment = BillPayment.objects.create(
                wallet=wallet,
                category=category,
                provider_name=provider_name,
                account_number=account_number,
                customer_name=customer_name,
                amount=amount,
                status="SUCCESS",  # In production, this would be PENDING until provider confirms
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
                type="BILLPAY",
                amount=-amount,  # Negative for debit
                balance_after=wallet.balance,
                status="SUCCESS",
                reference=reference,
                metadata={
                    'bill_payment_id': str(bill_payment.id),
                    'category': category,
                    'provider': provider_name,
                    'account_number': account_number,
                    'customer_name': customer_name
                }
            )

            # Mark as completed (in production, wait for provider webhook)
            from django.utils import timezone
            bill_payment.completed_at = timezone.now()
            bill_payment.save()

        return bill_payment
