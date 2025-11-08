"""

User Serializers - Profile & User Management

"""

from rest_framework import serializers

from django.contrib.auth import get_user_model

 

User = get_user_model()

 

 

class UserProfileSerializer(serializers.ModelSerializer):

    """

    Serializer for viewing user profile details.

    Excludes sensitive information like password.

    """

    wallet_balance = serializers.SerializerMethodField()

 

    class Meta:

        model = User

        fields = [

            'id',

            'username',

            'phone',

            'role',

            'is_verified',

            'is_active',

            'date_joined',

            'wallet_balance',

        ]

        read_only_fields = ['id', 'date_joined', 'is_verified']

 

    def get_wallet_balance(self, obj):

        """Get user's wallet balance if wallet exists"""

        if hasattr(obj, 'wallet'):

            return str(obj.wallet.balance)

        return "0.00"

 

 

class UserUpdateSerializer(serializers.ModelSerializer):

    """

    Serializer for updating user profile.

    Only allows updating specific fields.

    """

    class Meta:

        model = User

        fields = ['username']

 

    def validate_username(self, value):

        """Ensure username is unique (excluding current user)"""

        user = self.context['request'].user

        if User.objects.exclude(pk=user.pk).filter(username=value).exists():

            raise serializers.ValidationError("This username is already taken.")

        return value

 

 

class UserListSerializer(serializers.ModelSerializer):

    """

    Minimal serializer for listing users (admin/search purposes).

    """

    class Meta:

        model = User

        fields = ['id', 'username', 'phone', 'role', 'is_verified']

        read_only_fields = fields

 

