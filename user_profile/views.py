from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import APIException
from django.contrib.auth import get_user_model
from .utils import generate_and_save_otp

User = get_user_model()

class LoginAPIView(APIView):

    def post(self, request, *args, **kwargs):
        phone = request.data.get('phone')

        # Check if phone number is provided
        if not phone:
            raise APIException({'msg': 'Phone number is required.', 'request_status': 0})

        # Try to retrieve the user with the given phone number
        user = User.objects.filter(phone=phone).first()

        if user:
            # Generate OTP for existing user
            otp_code = generate_and_save_otp(user)

            data = {
                "phone": user.phone,
                "otp": otp_code,
                "step": "login",
                'request_status': 1,
                "msg": "OTP sent successfully"
            }
            return Response(data, status=status.HTTP_200_OK)

        else:
            # If user does not exist, create a new account and generate OTP
            try:
                user = User.objects.create(phone=phone, is_verified=False)
                otp_code = generate_and_save_otp(user)
            except Exception as e:
                raise APIException({'msg': str(e), 'request_status': 0})

            data = {
                "phone": user.phone,
                "otp": otp_code,
                "step": "signup",
                'request_status': 1,
                "msg": "Account created successfully. OTP sent for verification."
            }
            return Response(data, status=status.HTTP_201_CREATED)
