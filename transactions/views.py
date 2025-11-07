"""
Transaction Views
"""
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, OpenApiParameter

from .models import Transaction
from .serializers import TransactionSerializer


class TransactionListView(APIView):
    """
    List user's transaction history
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(
        parameters=[
            OpenApiParameter(name='type', description='Filter by transaction type (TOPUP, TRANSFER, WITHDRAW, BILLPAY)', required=False, type=str),
            OpenApiParameter(name='status', description='Filter by status (PENDING, SUCCESS, FAILED)', required=False, type=str),
        ],
        responses={
            200: TransactionSerializer(many=True),
        },
        description="Get authenticated user's transaction history with optional filters"
    )
    def get(self, request):
        user_wallet = request.user.wallet

        # Get all transactions for user's wallet
        transactions = Transaction.objects.filter(wallet=user_wallet)

        # Apply filters if provided
        transaction_type = request.query_params.get('type', None)
        if transaction_type:
            transactions = transactions.filter(type=transaction_type.upper())

        transaction_status = request.query_params.get('status', None)
        if transaction_status:
            transactions = transactions.filter(status=transaction_status.upper())

        # Order by most recent first
        transactions = transactions.order_by('-created_at')

        serializer = TransactionSerializer(transactions, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
