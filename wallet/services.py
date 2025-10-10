from notifications.services import send_notification

# Example in wallet/services.py
def transfer_funds(sender, receiver, amount):
    ...
    send_notification(
        user=sender.user,
        title="Transfer Successful 💸",
        message=f"You sent {amount} MRU to {receiver.user.username}.",
        channel="INAPP",
        metadata={"type": "transfer"}
    )

    send_notification(
        user=receiver.user,
        title="You Received Money 💰",
        message=f"{sender.user.username} sent you {amount} MRU.",
        channel="INAPP",
        metadata={"type": "transfer"}
    )
