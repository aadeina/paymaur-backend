"""

Wallet Serializers - Wallet Management

"""

from rest_framework import serializers

from .models import Wallet

from django.contrib.auth import get_user_model

 

User = get_user_model()

 

 

class WalletSerializer(serializers.ModelSerializer):

    """

    Serializer for wallet information.

    """

    user_info = serializers.SerializerMethodField()

 

    class Meta:

        model = Wallet

        fields = [

            'id',

            'user_info',

            'balance',

            'is_locked',

            'last_updated',

        ]

        read_only_fields = ['id', 'balance', 'last_updated']

 

    def get_user_info(self, obj):

        """Return basic user information"""

        return {

            'id': str(obj.user.id),

            'username': obj.user.username,

            'phone': obj.user.phone,

        }

 

 

class WalletBalanceSerializer(serializers.ModelSerializer):

    """

    Minimal serializer for just checking balance.

    """

    class Meta:

        model = Wallet

        fields = ['balance', 'is_locked', 'last_updated']

        read_only_fields = fields

 