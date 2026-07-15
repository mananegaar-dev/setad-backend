from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from rest_framework import status
from django.contrib.auth import get_user_model
import secrets
import requests
from auth_app.models.otp import Otp
from rest_framework.permissions import IsAuthenticated

User = get_user_model()
OTP_API = "https://api.sms.ir/v1/send/verify/"
X_API_KEY = "2BuRFGsX4cOTkGUglg3IZjK9Bv2x6lSeC01UZVhD4v9hJb9P"
OTP_TEMPlATE_ID = 634505
NAME = "OTP"


@extend_schema(
    summary="ارسال کد امنیتی (OTP)",
    description="بررسی نام کاربری و رمز عبور و ارسال کد یکبار مصرف به شماره کاربر",
    tags=["Auth"],
    request={
        "application/json": {
            "type": "object",
            "properties": {
                "username": {"type": "string"},
                "password": {"type": "string"},
            },
            "required": ["username", "password"],
        }
    },
)
class UserLoginView(APIView):

    permission_classes = [AllowAny]

    def post(self, request):

        username = request.data.get("username")
        password = request.data.get("password")

        user = authenticate(username=username, password=password)

        if not user:
            return Response(
                {"message": "نام کاربری یا رمز عبور اشتباه است."},
                status=status.HTTP_400_BAD_REQUEST
            )

        user = User.objects.get(username=username)
        phone_number = user.phone_number

        otp_code = str(secrets.randbelow(900000) + 100000)

        otp_instance = Otp.objects.create(user=user, code=otp_code)

        try:
            headers = {
                "X-API-KEY": X_API_KEY,
                "Content-Type": "application/json",
                "Accept": "application/json"
            }

            data = {
                "Mobile": phone_number,
                "TemplateId": OTP_TEMPlATE_ID,
                "Parameters": [
                    {
                        "Name": NAME,
                        "Value": otp_code
                    }
                ]
            }

            response = requests.post(OTP_API, json=data, headers=headers, timeout=10)
            response.raise_for_status()
            return Response(
                {
                    "message": "کد امنیتی ارسال شد",
                    "otp_id": str(otp_instance.otp_id),
                },
                status=status.HTTP_200_OK
            )

        except requests.RequestException as e:
            return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    summary="تایید کد امنیتی و ورود",
    description="بررسی کد یکبار مصرف با استفاده از شناسه دریافتی از مرحله ارسال و در صورت صحیح بودن صدور توکن‌های ورود",
    tags=["Auth"],
    request={
        "application/json": {
            "type": "object",
            "properties": {
                "otp_id": {"type": "string"},
                "otp": {"type": "string"},
            },
            "required": ["otp_id", "otp"],
        }
    },
)
class OtpVerifyView(APIView):

    permission_classes = [AllowAny]

    def post(self, request):

        otp_id = request.data.get("otp_id")
        otp_code = request.data.get("otp")

        if not otp_id or not otp_code:
            return Response(
                {"message": "شناسه کد امنیتی و کد امنیتی الزامی هستند."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            otp = Otp.objects.get(otp_id=otp_id, is_used=False)
        except (Otp.DoesNotExist, ValueError):
            return Response(
                {"message": "کد امنیتی معتبر یافت نشد."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if otp.is_expired():
            return Response(
                {"message": "کد امنیتی منقضی شده است."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if otp.code != str(otp_code):
            return Response(
                {"message": "کد امنیتی اشتباه است."},
                status=status.HTTP_400_BAD_REQUEST
            )

        user = otp.user
        otp.is_used = True
        otp.save()

        refresh = RefreshToken.for_user(user)
        access = str(refresh.access_token)

        response = Response(
            {
                "message": "با موفقیت وارد شدید",
                "refresh": str(refresh),
                "access": access,
            },
            status=status.HTTP_200_OK,
        )

        response.set_cookie(
            "access",
            access,
            httponly=True,
            secure=False,
            samesite="Lax",
        )

        response.set_cookie(
            "refresh",
            str(refresh),
            httponly=True,
            secure=False,
            samesite="Lax",
        )

        return response


@extend_schema(
    summary="لاگیم بودن یا نبودن کاربر",
    tags=["Auth"],
)
class IsLogin(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        return Response({"message": "ok"}, status=200)
