"""

Transaction Views - Transaction History & Management

"""

from rest_framework import generics, status

from rest_framework.permissions import IsAuthenticated

from rest_framework.response import Response

from rest_framework.views import APIView

from django.db.models import Sum, Count, Q

from .models import Transaction

from .serializers import (

    TransactionSerializer,

    TransactionListSerializer,

    TransactionStatsSerializer,

)

 

 

class TransactionListView(generics.ListAPIView):

    """

    GET /api/v1/transactions/

 

    List all transactions for the authenticated user's wallet.

    Supports filtering by type and status.

    """

    serializer_class = TransactionListSerializer

    permission_classes = [IsAuthenticated]

 

    def get_queryset(self):

        user = self.request.user

        if not hasattr(user, 'wallet'):

            return Transaction.objects.none()

 

        queryset = Transaction.objects.filter(wallet=user.wallet)

 

        # Filter by type

        transaction_type = self.request.query_params.get('type', None)

        if transaction_type:

            queryset = queryset.filter(type=transaction_type)

 

        # Filter by status

        transaction_status = self.request.query_params.get('status', None)

        if transaction_status:

            queryset = queryset.filter(status=transaction_status)

 

        return queryset.order_by('-created_at')

 

 

class TransactionDetailView(generics.RetrieveAPIView):

    """

    GET /api/v1/transactions/<id>/

 

    Retrieve detailed information about a specific transaction.

    """

    serializer_class = TransactionSerializer

    permission_classes = [IsAuthenticated]

 

    def get_queryset(self):

        user = self.request.user

        if not hasattr(user, 'wallet'):

            return Transaction.objects.none()

        return Transaction.objects.filter(wallet=user.wallet)

 

 

class TransactionStatsView(APIView):

    """

    GET /api/v1/transactions/stats/

 

    Get transaction statistics for the authenticated user.

    """

    permission_classes = [IsAuthenticated]

 

    def get(self, request):

        user = request.user

        if not hasattr(user, 'wallet'):

            return Response({

                'total_transactions': 0,

                'total_spent': '0.00',

                'total_received': '0.00',

                'pending_count': 0,

                'success_count': 0,

                'failed_count': 0,

            })

 

        wallet = user.wallet

        transactions = Transaction.objects.filter(wallet=wallet)

 

        # Calculate stats

        total_transactions = transactions.count()

 

        # Total spent (negative transactions: transfers, withdrawals, bills)

        total_spent = transactions.filter(

            type__in=['TRANSFER', 'WITHDRAW', 'BILLPAY']

        ).aggregate(total=Sum('amount'))['total'] or 0

 

        # Total received (positive transactions: top-ups)

        total_received = transactions.filter(

            type='TOPUP'

        ).aggregate(total=Sum('amount'))['total'] or 0

 

        # Status counts

        status_counts = transactions.values('status').annotate(count=Count('id'))

        pending_count = next((item['count'] for item in status_counts if item['status'] == 'PENDING'), 0)

        success_count = next((item['count'] for item in status_counts if item['status'] == 'SUCCESS'), 0)

        failed_count = next((item['count'] for item in status_counts if item['status'] == 'FAILED'), 0)

 

        stats = {

            'total_transactions': total_transactions,

            'total_spent': str(total_spent),

            'total_received': str(total_received),

            'pending_count': pending_count,

            'success_count': success_count,

            'failed_count': failed_count,

        }

 

        serializer = TransactionStatsSerializer(stats)

        return Response(serializer.data)

 

 

class RecentTransactionsView(generics.ListAPIView):

    """

    GET /api/v1/transactions/recent/

 

    Get the 10 most recent transactions.

    """

    serializer_class = TransactionListSerializer

    permission_classes = [IsAuthenticated]

 

    def get_queryset(self):

        user = self.request.user

        if not hasattr(user, 'wallet'):

            return Transaction.objects.none()

        return Transaction.objects.filter(

            wallet=user.wallet

        ).order_by('-created_at')[:10]

 