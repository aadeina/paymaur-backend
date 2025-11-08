"""
Top-up URL Configuration
"""
from django.urls import path
from .views import TopupCreateView, TopupListView

app_name = 'topup'

urlpatterns = [
    path('', TopupListView.as_view(), name='topup-list'),
    path('create/', TopupCreateView.as_view(), name='topup-create'),
]
