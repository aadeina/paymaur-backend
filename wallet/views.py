"""
Wallet Views
"""
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, OpenApiResponse

from .models import Wallet
from .serializers import WalletSerializer


class WalletDetailView(APIView):
    """
    Get current user's wallet information
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={
            200: WalletSerializer,
            404: OpenApiResponse(description="Wallet not found")
        },
        description="Get authenticated user's wallet balance and information"
    )
    def get(self, request):
        try:
            wallet = request.user.wallet
            serializer = WalletSerializer(wallet)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Wallet.DoesNotExist:
            return Response(
                {"error": "Wallet not found"},
                status=status.HTTP_404_NOT_FOUND
            )
