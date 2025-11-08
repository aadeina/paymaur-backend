"""
Agent URL Configuration
"""
from django.urls import path
from .views import (
    CashInView,
    CashOutRequestView,
    CashOutCompleteView,
    AgentTransactionListView,
    AgentListView
)

app_name = 'agents'

urlpatterns = [
    path('', AgentListView.as_view(), name='agent-list'),
    path('cash-in/', CashInView.as_view(), name='cash-in'),
    path('cash-out/request/', CashOutRequestView.as_view(), name='cash-out-request'),
    path('cash-out/complete/', CashOutCompleteView.as_view(), name='cash-out-complete'),
    path('transactions/', AgentTransactionListView.as_view(), name='agent-transactions'),
]
