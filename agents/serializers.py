"""
Agent Serializers
Cash-in and cash-out operations through agents
"""
from rest_framework import serializers
from decimal import Decimal
from django.db import transaction as db_transaction
import uuid
import random

from .models import Agent, AgentTransaction
from transactions.models import Transaction
from users.models import User


class AgentSerializer(serializers.ModelSerializer):
    """
    Agent information serializer
    """
    username = serializers.CharField(source='user.username', read_only=True)
    phone = serializers.CharField(source='user.phone', read_only=True)

    class Meta:
        model = Agent
        fields = ['id', 'username', 'phone', 'name', 'location', 'latitude', 'longitude', 'is_active', 'created_at']
        read_only_fields = ['id', 'created_at']


class AgentTransactionSerializer(serializers.ModelSerializer):
    """
    Agent transaction serializer
    """
    agent_name = serializers.CharField(source='agent.name', read_only=True)
    wallet_owner = serializers.CharField(source='wallet.user.username', read_only=True)

    class Meta:
        model = AgentTransaction
        fields = ['id', 'agent_name', 'wallet_owner', 'type', 'amount', 'status', 'token', 'reference', 'idempotency_key', 'metadata', 'created_at', 'completed_at']
        read_only_fields = ['id', 'status', 'token', 'reference', 'idempotency_key', 'created_at', 'completed_at']


class CashInSerializer(serializers.Serializer):
    """
    Cash-in: Customer gives cash to agent, wallet gets credited
    """
    customer_phone = serializers.CharField(
        max_length=8,
        min_length=8,
        help_text="Customer's phone number"
    )
    amount = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        min_value=Decimal('10.00'),
        max_value=Decimal('100000.00'),
        help_text="Amount to deposit (10-100000 MRU)"
    )

    def create(self, validated_data):
        """
        Execute cash-in: Add money to customer's wallet
        Agent user must have agent profile
        """
        agent_user = self.context['request'].user

        # Verify user is an agent
        try:
            agent = agent_user.agent_profile
        except:
            raise serializers.ValidationError("User is not registered as an agent")

        if not agent.is_active:
            raise serializers.ValidationError("Agent account is not active")

        customer_phone = validated_data['customer_phone']
        amount = validated_data['amount']

        # Find customer
        try:
            customer_user = User.objects.get(phone=customer_phone)
        except User.DoesNotExist:
            raise serializers.ValidationError({"customer_phone": "Customer not found with this phone number"})

        customer_wallet = customer_user.wallet

        if customer_wallet.is_locked:
            raise serializers.ValidationError("Customer's wallet is locked")

        # Execute cash-in atomically
        with db_transaction.atomic():
            # Generate unique references
            reference = f"CASHIN-{uuid.uuid4().hex[:12].upper()}"
            token = f"{random.randint(10000000, 99999999)}"  # 8-digit token
            idempotency_key = f"{agent_user.id}-{customer_phone}-{amount}-{uuid.uuid4().hex[:8]}"

            # Credit customer wallet
            customer_wallet.balance += amount
            customer_wallet.save()

            # Create agent transaction record
            agent_txn = AgentTransaction.objects.create(
                agent=agent,
                wallet=customer_wallet,
                type="CASHIN",
                amount=amount,
                status="SUCCESS",
                token=token,
                reference=reference,
                idempotency_key=idempotency_key,
                metadata={
                    'agent_name': agent.name,
                    'agent_location': agent.location,
                    'customer': customer_user.username
                }
            )

            # Create transaction record for customer
            Transaction.objects.create(
                wallet=customer_wallet,
                type="TOPUP",  # Cash-in is a type of top-up
                amount=amount,  # Positive for credit
                balance_after=customer_wallet.balance,
                status="SUCCESS",
                reference=reference,
                metadata={
                    'agent_transaction_id': str(agent_txn.id),
                    'type': 'cash_in',
                    'agent': agent.name,
                    'agent_location': agent.location
                }
            )

            # Mark as completed
            from django.utils import timezone
            agent_txn.completed_at = timezone.now()
            agent_txn.save()

        return agent_txn


class CashOutRequestSerializer(serializers.Serializer):
    """
    Cash-out request: Customer requests to withdraw cash, gets a token
    """
    amount = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        min_value=Decimal('10.00'),
        max_value=Decimal('100000.00'),
        help_text="Amount to withdraw (10-100000 MRU)"
    )

    def create(self, validated_data):
        """
        Create cash-out request and generate token
        Wallet is debited immediately, customer takes token to agent
        """
        customer_user = self.context['request'].user
        customer_wallet = customer_user.wallet

        amount = validated_data['amount']

        # Validation
        if customer_wallet.is_locked:
            raise serializers.ValidationError("Your wallet is locked")

        if customer_wallet.balance < amount:
            raise serializers.ValidationError(
                f"Insufficient balance. Available: {customer_wallet.balance} MRU"
            )

        # Execute cash-out request atomically
        with db_transaction.atomic():
            # Generate unique references and token
            reference = f"CASHOUT-{uuid.uuid4().hex[:12].upper()}"
            token = f"{random.randint(10000000, 99999999)}"  # 8-digit token
            idempotency_key = f"{customer_user.id}-cashout-{amount}-{uuid.uuid4().hex[:8]}"

            # Debit customer wallet immediately
            customer_wallet.balance -= amount
            customer_wallet.save()

            # Create agent transaction record (PENDING until agent confirms)
            # We'll create a placeholder agent transaction
            agent_txn = AgentTransaction.objects.create(
                agent=None,  # Will be filled when agent processes
                wallet=customer_wallet,
                type="CASHOUT",
                amount=amount,
                status="PENDING",  # Waiting for agent to complete
                token=token,
                reference=reference,
                idempotency_key=idempotency_key,
                metadata={
                    'customer': customer_user.username,
                    'customer_phone': customer_user.phone,
                    'status_note': 'Waiting for agent to process with token'
                }
            )

            # Create transaction record
            Transaction.objects.create(
                wallet=customer_wallet,
                type="WITHDRAW",
                amount=-amount,  # Negative for debit
                balance_after=customer_wallet.balance,
                status="PENDING",
                reference=reference,
                metadata={
                    'agent_transaction_id': str(agent_txn.id),
                    'type': 'cash_out_request',
                    'token': token,
                    'note': 'Take this token to any agent to collect cash'
                }
            )

        return agent_txn


class CashOutCompleteSerializer(serializers.Serializer):
    """
    Complete cash-out: Agent verifies token and gives cash to customer
    """
    token = serializers.CharField(
        max_length=8,
        min_length=8,
        help_text="8-digit token from customer"
    )

    def create(self, validated_data):
        """
        Agent completes cash-out by providing token
        """
        agent_user = self.context['request'].user

        # Verify user is an agent
        try:
            agent = agent_user.agent_profile
        except:
            raise serializers.ValidationError("User is not registered as an agent")

        if not agent.is_active:
            raise serializers.ValidationError("Agent account is not active")

        token = validated_data['token']

        # Find pending cash-out transaction with this token
        try:
            agent_txn = AgentTransaction.objects.get(token=token, type="CASHOUT", status="PENDING")
        except AgentTransaction.DoesNotExist:
            raise serializers.ValidationError({"token": "Invalid or already processed token"})

        # Complete the transaction
        with db_transaction.atomic():
            # Update agent transaction
            agent_txn.agent = agent
            agent_txn.status = "SUCCESS"
            agent_txn.metadata.update({
                'agent_name': agent.name,
                'agent_location': agent.location,
                'completed_by': agent_user.username
            })

            from django.utils import timezone
            agent_txn.completed_at = timezone.now()
            agent_txn.save()

            # Update transaction status
            Transaction.objects.filter(reference=agent_txn.reference).update(status="SUCCESS")

        return agent_txn
