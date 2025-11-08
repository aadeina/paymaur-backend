"""
Bill Payment URL Configuration
"""
from django.urls import path
from .views import BillPaymentCreateView, BillPaymentListView

app_name = 'bills'

urlpatterns = [
    path('', BillPaymentListView.as_view(), name='bill-list'),
    path('create/', BillPaymentCreateView.as_view(), name='bill-create'),
]
