from django.urls import path
from .views import MyWalletView, MyTransactionsView, AdminTopUpView

urlpatterns = [
    path('me/', MyWalletView.as_view(), name='my-wallet'),
    path('transactions/', MyTransactionsView.as_view(), name='my-transactions'),
    path('admin/topup/', AdminTopUpView.as_view(), name='admin-topup'),
]
