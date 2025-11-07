# authentication/otp_service.py
import random
from django.utils import timezone
from .models import OTP

def generate_otp(user, purpose):
    code = str(random.randint(100000, 999999))
    OTP.objects.create(user=user, code=code, purpose=purpose)
    print(f"DEBUG OTP for {user.phone}: {code}")  # 🔐 Replace with SMS API later
    return code

def verify_otp(user, code, purpose):
    otp = OTP.objects.filter(user=user, code=code, purpose=purpose, is_used=False).last()
    if not otp:
        return False, "Invalid or expired OTP"

    if otp.is_expired():
        return False, "OTP expired"

    otp.is_used = True
    otp.save()
    return True, "OTP verified successfully"
