from django.contrib import admin
from .models import Wallet


@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    list_display = ['user', 'balance', 'is_locked', 'last_updated']
    list_filter = ['is_locked', 'last_updated']
    search_fields = ['user__username', 'user__phone']
    readonly_fields = ['id', 'last_updated']
    ordering = ['-last_updated']
