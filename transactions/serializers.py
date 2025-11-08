"""

Transaction Serializers - Transaction History & Management

"""

from rest_framework import serializers

from .models import Transaction

 

 

class TransactionSerializer(serializers.ModelSerializer):

    """

    Serializer for transaction details.

    """

    wallet_owner = serializers.SerializerMethodField()

 

    class Meta:

        model = Transaction

        fields = [

            'id',

            'wallet',

            'wallet_owner',

            'type',

            'amount',

            'balance_after',

            'status',

            'reference',

            'metadata',

            'created_at',

        ]

        read_only_fields = fields

 

    def get_wallet_owner(self, obj):

        """Return wallet owner info"""

        return {

            'username': obj.wallet.user.username,

            'phone': obj.wallet.user.phone,

        }

 

 

class TransactionListSerializer(serializers.ModelSerializer):

    """

    Minimal serializer for transaction lists.

    """

    class Meta:

        model = Transaction

        fields = [

            'id',

            'type',

            'amount',

            'status',

            'reference',

            'created_at',

        ]

        read_only_fields = fields

 

 

class TransactionStatsSerializer(serializers.Serializer):

    """

    Serializer for transaction statistics.

    """

    total_transactions = serializers.IntegerField()

    total_spent = serializers.DecimalField(max_digits=12, decimal_places=2)

    total_received = serializers.DecimalField(max_digits=12, decimal_places=2)

    pending_count = serializers.IntegerField()

    success_count = serializers.IntegerField()

    failed_count = serializers.IntegerField()

 