"""
Agent Views
Cash-in and cash-out operations
"""
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, OpenApiResponse

from .models import Agent, AgentTransaction
from .serializers import (
    AgentSerializer,
    AgentTransactionSerializer,
    CashInSerializer,
    CashOutRequestSerializer,
    CashOutCompleteSerializer
)


class CashInView(APIView):
    """
    Cash-In: Agent deposits cash into customer wallet
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=CashInSerializer,
        responses={
            201: AgentTransactionSerializer,
            400: OpenApiResponse(description="Validation error")
        },
        description="Agent deposits cash into customer's wallet (Agent only)"
    )
    def post(self, request):
        serializer = CashInSerializer(data=request.data, context={'request': request})

        if serializer.is_valid():
            try:
                agent_txn = serializer.save()
                response_serializer = AgentTransactionSerializer(agent_txn)
                return Response(response_serializer.data, status=status.HTTP_201_CREATED)
            except Exception as e:
                return Response(
                    {"error": str(e)},
                    status=status.HTTP_400_BAD_REQUEST
                )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CashOutRequestView(APIView):
    """
    Cash-Out Request: Customer requests to withdraw cash and gets a token
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=CashOutRequestSerializer,
        responses={
            201: AgentTransactionSerializer,
            400: OpenApiResponse(description="Validation error or insufficient balance")
        },
        description="Request cash withdrawal - generates token to take to agent"
    )
    def post(self, request):
        serializer = CashOutRequestSerializer(data=request.data, context={'request': request})

        if serializer.is_valid():
            try:
                agent_txn = serializer.save()
                response_serializer = AgentTransactionSerializer(agent_txn)
                return Response({
                    **response_serializer.data,
                    "message": f"Cash-out request created. Token: {agent_txn.token}. Take this token to any agent to collect your cash."
                }, status=status.HTTP_201_CREATED)
            except Exception as e:
                return Response(
                    {"error": str(e)},
                    status=status.HTTP_400_BAD_REQUEST
                )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CashOutCompleteView(APIView):
    """
    Complete Cash-Out: Agent verifies token and completes withdrawal
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=CashOutCompleteSerializer,
        responses={
            200: AgentTransactionSerializer,
            400: OpenApiResponse(description="Invalid token or validation error")
        },
        description="Agent completes cash-out transaction with customer's token (Agent only)"
    )
    def post(self, request):
        serializer = CashOutCompleteSerializer(data=request.data, context={'request': request})

        if serializer.is_valid():
            try:
                agent_txn = serializer.save()
                response_serializer = AgentTransactionSerializer(agent_txn)
                return Response({
                    **response_serializer.data,
                    "message": "Cash-out completed successfully. Give cash to customer."
                }, status=status.HTTP_200_OK)
            except Exception as e:
                return Response(
                    {"error": str(e)},
                    status=status.HTTP_400_BAD_REQUEST
                )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AgentTransactionListView(APIView):
    """
    List agent transactions
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={
            200: AgentTransactionSerializer(many=True),
        },
        description="Get authenticated user's agent transaction history (customers see their cash-in/out, agents see their operations)"
    )
    def get(self, request):
        user = request.user

        # Check if user is an agent
        try:
            agent = user.agent_profile
            # Agent sees all their transactions
            transactions = AgentTransaction.objects.filter(agent=agent)
        except:
            # Customer sees their cash-in/out transactions
            wallet = user.wallet
            transactions = AgentTransaction.objects.filter(wallet=wallet)

        transactions = transactions.order_by('-created_at')

        serializer = AgentTransactionSerializer(transactions, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class AgentListView(APIView):
    """
    List all active agents
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={
            200: AgentSerializer(many=True),
        },
        description="Get list of all active agents with their locations"
    )
    def get(self, request):
        agents = Agent.objects.filter(is_active=True).order_by('name')
        serializer = AgentSerializer(agents, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
