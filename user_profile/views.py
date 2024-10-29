from django.contrib.auth import get_user_model
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import APIException
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework import status
from django.db import transaction
from .serializers import *
from .models import CustomUser
from user_profile.models import *
from .utils import generate_and_save_otp

User = get_user_model()

class LoginAPIView(APIView):

    def post(self, request, *args, **kwargs):
        phone = request.data.get('phone')

        # Check if phone number is provided
        if not phone:
            return Response({
                'results': {
                    'Data': {},
                    'request_status': 0,
                    "msg": "Phone number is required",
                    'status': 400
                }
            }, status=status.HTTP_400_BAD_REQUEST)

        # Try to retrieve the user with the given phone number
        user = User.objects.filter(phone=phone).first()

        if user:
            # Generate OTP for existing user
            otp_code = generate_and_save_otp(user)

            data = {
                "phone": user.phone,
                "otp": otp_code,
                "step": "login",
            }
            response_data = {
                'results': {
                    'Data': data,
                    'request_status': 1,
                    "msg": "OTP sent successfully",
                    'status': 200
                }
            }
            return Response(response_data, status=status.HTTP_200_OK)

        else:
            # If user does not exist, create a new account and generate OTP
            try:
                user = User.objects.create(phone=phone, is_verified=False)
                otp_code = generate_and_save_otp(user)
            except Exception as e:
                # raise APIException({'msg': str(e), 'request_status': 0})
                return Response({
                    'results': {
                        'Data': {},
                        'request_status': 0,
                        "msg": str(e),
                        'status': 400
                    }
                }, status=status.HTTP_400_BAD_REQUEST)

            data = {
                "phone": user.phone,
                "otp": otp_code,
                "step": "signup",
            }

            response_data = {
                'results': {
                    'Data': data,
                    'request_status': 1,
                    "msg": "Account created successfully. OTP sent for verification.",
                    'status': 200
                }
            }
            return Response(response_data, status=status.HTTP_200_OK)



class OTPVerificationAPIView(APIView):
    def post(self, request, *args, **kwargs):
        phone = request.data.get("phone")
        otp_code = request.data.get("otp_code")

        if not phone or not otp_code:
            return Response({
                'results': {
                    'Data': {},
                    'request_status': 0,
                    "msg": "Phone and OTP code are required",
                    'status': 400
                }
            }, status=status.HTTP_400_BAD_REQUEST)

        # Get the user by phone number
        try:
            user = User.objects.get(phone=phone)
        except User.DoesNotExist:
            return Response({
                'results': {
                    'Data': {},
                    'request_status': 0,
                    "msg": "User with this phone number does not exist",
                    'status': 404
                }
            }, status=status.HTTP_404_NOT_FOUND)

        # Check if an OTP exists and is valid
        otp = OTP.objects.filter(user=user, otp_code=otp_code).first()


        if otp and otp.is_valid():
            with transaction.atomic():
                # Update user fields to mark as active and verified
                user.is_active = True
                user.is_verified = True
                user.save()

                # Delete any existing token and create a new one
                Token.objects.filter(user=user).delete()
                token = Token.objects.create(user=user)

            data = {
                "phone": user.phone,
                "token": token.key
            }
            response_data = {
                'results': {
                    'Data': data,
                    'request_status': 1,
                    "msg": "OTP verified successfully",
                    'status': 200
                }
            }
            return Response(response_data, status=status.HTTP_200_OK)


        # OTP is invalid or expired
        return Response({
            'results': {
                'Data': {},
                'request_status': 0,
                "msg": "Invalid or expired OTP",
                'status': 400
            }
        }, status=status.HTTP_400_BAD_REQUEST)


class UserProfileAPIView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        # Serialize the authenticated user data
        serializer = UserProfileSerializer(request.user)
        data = {
            'results': {
                'Data': serializer.data,
                'request_status': 1,
                'msg': "User profile retrieved successfully",
                'status': 200
            }
        }
        return Response(data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        serializer = UserProfileSerializer(instance=request.user, data=request.data)

        if serializer.is_valid():
            # Update the user's profile
            serializer.save()
            response_data = {
                'results': {
                    'Data': serializer.data,
                    'request_status': 1,
                    'msg': "Profile updated successfully",
                    'status': 200
                }
            }
            return Response(response_data, status=status.HTTP_200_OK)

        # If the data is invalid, return a 400 response with error details
        response_data = {
            'results': {
                'Data': {},
                'request_status': 0,
                'msg': serializer.errors,
                'status': 400
            }
        }
        return Response(response_data, status=status.HTTP_400_BAD_REQUEST)