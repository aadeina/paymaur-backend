"""
Transfer URL Configuration
"""
from django.urls import path
from .views import TransferCreateView, TransferListView

app_name = 'transfers'

urlpatterns = [
    path('', TransferListView.as_view(), name='transfer-list'),
    path('create/', TransferCreateView.as_view(), name='transfer-create'),
]
