"""

Transaction URLs

"""

from django.urls import path

from .views import (

    TransactionListView,

    TransactionDetailView,

    TransactionStatsView,

    RecentTransactionsView,

)

 

app_name = 'transactions'

 

urlpatterns = [

    path('', TransactionListView.as_view(), name='transaction-list'),

    path('stats/', TransactionStatsView.as_view(), name='transaction-stats'),

    path('recent/', RecentTransactionsView.as_view(), name='recent-transactions'),

    path('<uuid:pk>/', TransactionDetailView.as_view(), name='transaction-detail'),

]

 