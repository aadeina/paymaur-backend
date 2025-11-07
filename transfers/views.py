"""
Transfer Views
"""
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, OpenApiResponse

from .models import Transfer
from .serializers import TransferSerializer, CreateTransferSerializer


class TransferCreateView(APIView):
    """
    Create a new money transfer
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=CreateTransferSerializer,
        responses={
            201: TransferSerializer,
            400: OpenApiResponse(description="Validation error or insufficient balance")
        },
        description="Transfer money to another user by username or phone number"
    )
    def post(self, request):
        serializer = CreateTransferSerializer(data=request.data, context={'request': request})

        if serializer.is_valid():
            try:
                transfer = serializer.save()
                response_serializer = TransferSerializer(transfer)
                return Response(response_serializer.data, status=status.HTTP_201_CREATED)
            except Exception as e:
                return Response(
                    {"error": str(e)},
                    status=status.HTTP_400_BAD_REQUEST
                )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TransferListView(APIView):
    """
    List user's transfer history
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={
            200: TransferSerializer(many=True),
        },
        description="Get authenticated user's transfer history (sent and received)"
    )
    def get(self, request):
        user_wallet = request.user.wallet

        # Get both sent and received transfers
        sent_transfers = Transfer.objects.filter(sender_wallet=user_wallet)
        received_transfers = Transfer.objects.filter(receiver_wallet=user_wallet)

        # Combine and order by date
        all_transfers = (sent_transfers | received_transfers).order_by('-created_at')

        serializer = TransferSerializer(all_transfers, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
