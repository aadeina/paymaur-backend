"""
Wallet URL Configuration
"""
from django.urls import path
from .views import WalletDetailView

app_name = 'wallet'

urlpatterns = [
    path('', WalletDetailView.as_view(), name='wallet-detail'),
]
