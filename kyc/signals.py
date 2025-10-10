from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import SimpleKYC

@receiver(post_save, sender=SimpleKYC)
def update_user_verification(sender, instance, **kwargs):
    """
    Automatically mark user as verified if KYC is verified.
    """
    if instance.status == "VERIFIED" and not instance.user.is_verified:
        instance.user.is_verified = True
        instance.user.save()
