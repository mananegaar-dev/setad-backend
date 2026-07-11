
from drf_spectacular.utils import extend_schema
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken



@extend_schema(
    summary="خروج کاربر",
    tags=["Auth"]
)
class LogoutView(APIView):

    permission_classes = [IsAuthenticated]


    def post(self, request):
        try:
            refresh_token = request.data["refresh"]

            token = RefreshToken(refresh_token)
            token.blacklist()

            return Response(
                {"message": "از حساب خارج شدید"},
                status=status.HTTP_205_RESET_CONTENT
            )

        except Exception:
            return Response(
                {"message": "توکن نا معتبر است"},
                status=status.HTTP_400_BAD_REQUEST
            )
