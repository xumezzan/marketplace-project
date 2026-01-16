from django.contrib import admin
from .models import Wallet, Transaction

@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    list_display = ('specialist', 'balance', 'currency')
    readonly_fields = ('balance',)

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('wallet', 'transaction_type', 'amount', 'created_at')
    list_filter = ('transaction_type',)
    readonly_fields = ('idempotency_key', 'wallet', 'amount', 'transaction_type')
