from drf_spectacular.utils import extend_schema
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from rest_framework import status
from django.contrib.auth import get_user_model
import secrets
import requests

from rest_framework.permissions import IsAuthenticated

User = get_user_model()
OTP_API="https://api.sms.ir/v1/send/verify/"
X_API_KEY="2BuRFGsX4cOTkGUglg3IZjK9Bv2x6lSeC01UZVhD4v9hJb9P"
OTP_TEMPlATE_ID=634505
NAME="OTP"
OTP_EXP=120


@extend_schema(
    summary="ورود کاربر",
    description="ورود با نام کاربری و رمز عبور و ذخیره توکن در کوکی",
    tags=["Auth"],
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

        otp = str(secrets.randbelow(900000) + 100000)

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
                        "Name": "OTP",
                        "Value": otp
                    }
                ]
            }

            response = requests.post(OTP_API, json=data, headers=headers, timeout=10)
            response.raise_for_status()
            return Response({"message": "کد امنیتی ارسال شد"}, status=status.HTTP_200_OK)

        except requests.RequestException as e:
            return Response({"message":str(e)}, status=status.HTTP_400_BAD_REQUEST)
        # refresh = RefreshToken.for_user(user)
        # access_token = str(refresh.access_token)

        # response = Response(
        #     {
        #     "message": "ورود با موفقیت انجام شد",
        #      "refresh":str(refresh),
        #      "access":access_token
        #      },
        #     status=status.HTTP_200_OK
        # )

        # response.set_cookie(
        #     key="access",
        #     value=access_token,
        #     httponly=True,
        #     secure=True,
        #     samesite="None",
        #     domain=".setadmahalle.ir"
        # )

        # response.set_cookie(
        #     key="refresh",
        #     value=str(refresh),
        #     httponly=True,
        #     secure=True,
        #     samesite="None",
        #     domain=".setadmahalle.ir"
        # )

        # return response
    


@extend_schema(
    summary="لاگیم بودن یا نبودن کاربر",
    tags=["Auth"],
)
class IsLogin(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, *args, **kwargs):
        return Response({"message": "ok"},status=200)