from django.urls import path
from user_profile.views import *

urlpatterns = [
    path('login/', LoginAPIView.as_view(), name='login'),
    path('verify-otp/', OTPVerificationAPIView.as_view(), name='verify-otp'),
]
