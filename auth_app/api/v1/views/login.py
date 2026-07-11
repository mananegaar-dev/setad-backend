from drf_spectacular.utils import extend_schema
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from rest_framework import status

from rest_framework.permissions import IsAuthenticated


@extend_schema(
    summary="ورود کاربر",
    description="ورود با نام کاربری و رمز عبور و ذخیره توکن در کوکی",
    tags=["Auth"],
)
class UserLoginView(APIView):

    permission_classes = [AllowAny]
    # authentication_classes = []

    def post(self, request):

        username = request.data.get("username")
        password = request.data.get("password")

        user = authenticate(username=username, password=password)

        if not user:
            return Response(
                {"message": "نام کاربری یا رمز عبور اشتباه است."},
                status=status.HTTP_400_BAD_REQUEST
            )

        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)

        response = Response(
            {
            "message": "ورود با موفقیت انجام شد",
             "refresh":str(refresh),
             "access":access_token
             },
            status=status.HTTP_200_OK
        )

        # response.set_cookie(
        #     key="access",
        #     value=access_token,
        #     httponly=True,
        #     secure=True,
        #     samesite="Lax"
        # )

        # response.set_cookie(
        #     key="refresh",
        #     value=str(refresh),
        #     httponly=True,
        #     secure=True,
        #     samesite="Lax"
        # )

        return response
    


@extend_schema(
    summary="لاگیم بودن یا نبودن کاربر",
    tags=["Auth"],
)
class IsLogin(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, *args, **kwargs):
        return Response({"message": "ok"},status=200)