import random
from django.utils import timezone
from datetime import timedelta
from .models import OTP

def generate_and_save_otp(user, expiry_minutes=5):
    """Generate a 6-digit OTP, save it to the OTP model, and set an expiration time."""
    otp_code = f"{random.randint(100000, 999999)}"
    expires_at = timezone.now() + timedelta(minutes=expiry_minutes)

    # Save the OTP instance
    OTP.objects.create(user=user, otp_code=otp_code, expires_at=expires_at)

    return otp_code