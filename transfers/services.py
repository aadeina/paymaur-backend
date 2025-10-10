from django.db import transaction as db_transaction
from wallet.models import Wallet
from transactions.models import Transaction
from .models import Transfer

@db_transaction.atomic
def perform_transfer(sender_wallet, receiver_wallet, amount, note=""):
    if sender_wallet.balance < amount:
        raise ValueError("Insufficient balance")

    # Deduct and credit
    sender_wallet.balance -= amount
    receiver_wallet.balance += amount
    sender_wallet.save()
    receiver_wallet.save()

    # Create the transfer record
    transfer = Transfer.objects.create(
        sender_wallet=sender_wallet,
        receiver_wallet=receiver_wallet,
        amount=amount,
        note=note,
        status="SUCCESS",
        reference=f"TXN-{uuid.uuid4().hex[:10].upper()}"
    )

    # Create corresponding transactions
    Transaction.objects.create(
        wallet=sender_wallet,
        type="TRANSFER",
        amount=amount,
        balance_after=sender_wallet.balance,
        status="SUCCESS",
        reference=f"DEBIT-{transfer.reference}",
        metadata={"to": receiver_wallet.user.phone}
    )

    Transaction.objects.create(
        wallet=receiver_wallet,
        type="TRANSFER",
        amount=amount,
        balance_after=receiver_wallet.balance,
        status="SUCCESS",
        reference=f"CREDIT-{transfer.reference}",
        metadata={"from": sender_wallet.user.phone}
    )

    return transfer
