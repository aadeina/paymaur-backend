"""
Top-up Views
Mobile recharge endpoints
"""
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiResponse

from .models import Topup
from .serializers import TopupSerializer, CreateTopupSerializer


class TopupCreateView(APIView):
    """
    Create a new mobile top-up/recharge
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=CreateTopupSerializer,
        responses={
            201: TopupSerializer,
            400: OpenApiResponse(description="Validation error or insufficient balance")
        },
        description="Recharge mobile phone for Mattel, Chinguitel, or Mauritel"
    )
    def post(self, request):
        serializer = CreateTopupSerializer(data=request.data, context={'request': request})

        if serializer.is_valid():
            try:
                topup = serializer.save()
                response_serializer = TopupSerializer(topup)
                return Response(response_serializer.data, status=status.HTTP_201_CREATED)
            except Exception as e:
                return Response(
                    {"error": str(e)},
                    status=status.HTTP_400_BAD_REQUEST
                )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TopupListView(APIView):
    """
    List user's top-up history
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(
        parameters=[
            OpenApiParameter(name='operator', description='Filter by operator (MATTEL, CHINGUITEL, MAURITEL)', required=False, type=str),
            OpenApiParameter(name='status', description='Filter by status (PENDING, SUCCESS, FAILED)', required=False, type=str),
        ],
        responses={
            200: TopupSerializer(many=True),
        },
        description="Get authenticated user's mobile top-up history with optional filters"
    )
    def get(self, request):
        user_wallet = request.user.wallet

        # Get all top-ups for user's wallet
        topups = Topup.objects.filter(wallet=user_wallet)

        # Apply filters
        operator = request.query_params.get('operator', None)
        if operator:
            topups = topups.filter(operator=operator.upper())

        topup_status = request.query_params.get('status', None)
        if topup_status:
            topups = topups.filter(status=topup_status.upper())

        # Order by most recent first
        topups = topups.order_by('-created_at')

        serializer = TopupSerializer(topups, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
