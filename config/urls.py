"""
PayMaur API URL Configuration
"""
from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),

    # API Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),

    # Authentication
    path('api/auth/', include('authentication.urls')),

    # Wallet & Transfers
    path('api/wallet/', include('wallet.urls')),
    path('api/transfers/', include('transfers.urls')),
    path('api/transactions/', include('transactions.urls')),

    # Services
    path('api/topup/', include('topup.urls')),
    path('api/bills/', include('bills.urls')),
    path('api/agents/', include('agents.urls')),
]
