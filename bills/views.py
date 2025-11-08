"""
Bill Payment Views
Utility bill payment endpoints
"""
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiResponse

from .models import BillPayment
from .serializers import BillPaymentSerializer, CreateBillPaymentSerializer


class BillPaymentCreateView(APIView):
    """
    Create a new bill payment
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=CreateBillPaymentSerializer,
        responses={
            201: BillPaymentSerializer,
            400: OpenApiResponse(description="Validation error or insufficient balance")
        },
        description="Pay utility bills (electricity, water, internet, TV, etc.)"
    )
    def post(self, request):
        serializer = CreateBillPaymentSerializer(data=request.data, context={'request': request})

        if serializer.is_valid():
            try:
                bill_payment = serializer.save()
                response_serializer = BillPaymentSerializer(bill_payment)
                return Response(response_serializer.data, status=status.HTTP_201_CREATED)
            except Exception as e:
                return Response(
                    {"error": str(e)},
                    status=status.HTTP_400_BAD_REQUEST
                )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BillPaymentListView(APIView):
    """
    List user's bill payment history
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(
        parameters=[
            OpenApiParameter(name='category', description='Filter by category (ELECTRICITY, WATER, INTERNET, TV, OTHER)', required=False, type=str),
            OpenApiParameter(name='status', description='Filter by status (PENDING, SUCCESS, FAILED)', required=False, type=str),
        ],
        responses={
            200: BillPaymentSerializer(many=True),
        },
        description="Get authenticated user's bill payment history with optional filters"
    )
    def get(self, request):
        user_wallet = request.user.wallet

        # Get all bill payments for user's wallet
        bill_payments = BillPayment.objects.filter(wallet=user_wallet)

        # Apply filters
        category = request.query_params.get('category', None)
        if category:
            bill_payments = bill_payments.filter(category=category.upper())

        bill_status = request.query_params.get('status', None)
        if bill_status:
            bill_payments = bill_payments.filter(status=bill_status.upper())

        # Order by most recent first
        bill_payments = bill_payments.order_by('-created_at')

        serializer = BillPaymentSerializer(bill_payments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
