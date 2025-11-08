"""

Wallet URLs

"""

from django.urls import path

from .views import (

    WalletDetailView,

    WalletBalanceView,

    WalletLockToggleView,

)

 

app_name = 'wallet'

 

urlpatterns = [

    path('', WalletDetailView.as_view(), name='wallet-detail'),

    path('balance/', WalletBalanceView.as_view(), name='wallet-balance'),

    path('<str:action>/', WalletLockToggleView.as_view(), name='wallet-lock-toggle'),

]

 