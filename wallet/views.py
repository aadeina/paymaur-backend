"""

Wallet Views - Wallet Management

"""

from rest_framework import generics, status

from rest_framework.permissions import IsAuthenticated

from rest_framework.response import Response

from rest_framework.views import APIView

from django.shortcuts import get_object_or_404

from .models import Wallet

from .serializers import WalletSerializer, WalletBalanceSerializer

 

 

class WalletDetailView(generics.RetrieveAPIView):

    """

    GET /api/v1/wallet/

 

    Retrieve the authenticated user's wallet details.

    """

    serializer_class = WalletSerializer

    permission_classes = [IsAuthenticated]

 

    def get_object(self):

        # Get or create wallet for the user

        wallet, created = Wallet.objects.get_or_create(user=self.request.user)

        return wallet

 

 

class WalletBalanceView(APIView):

    """

    GET /api/v1/wallet/balance/

 

    Get just the balance for quick checks.

    """

    permission_classes = [IsAuthenticated]

 

    def get(self, request):

        wallet, created = Wallet.objects.get_or_create(user=request.user)

        serializer = WalletBalanceSerializer(wallet)

        return Response(serializer.data)

 

 

class WalletLockToggleView(APIView):

    """

    POST /api/v1/wallet/lock/

    POST /api/v1/wallet/unlock/

 

    Lock or unlock wallet (security feature).

    """

    permission_classes = [IsAuthenticated]

 

    def post(self, request, action):

        wallet, created = Wallet.objects.get_or_create(user=request.user)

 

        if action == 'lock':

            if wallet.is_locked:

                return Response(

                    {'detail': 'Wallet is already locked.'},

                    status=status.HTTP_400_BAD_REQUEST

                )

            wallet.is_locked = True

            wallet.save()

            return Response(

                {'detail': 'Wallet locked successfully.', 'is_locked': True},

                status=status.HTTP_200_OK

            )

 

        elif action == 'unlock':

            if not wallet.is_locked:

                return Response(

                    {'detail': 'Wallet is already unlocked.'},

                    status=status.HTTP_400_BAD_REQUEST

                )

            wallet.is_locked = False

            wallet.save()

            return Response(

                {'detail': 'Wallet unlocked successfully.', 'is_locked': False},

                status=status.HTTP_200_OK

            )

 

        return Response(

            {'detail': 'Invalid action.'},

            status=status.HTTP_400_BAD_REQUEST

        )

 