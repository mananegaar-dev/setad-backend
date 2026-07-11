from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status
from drf_spectacular.utils import extend_schema



@extend_schema(
    summary="رفرش توکن",
    tags=["Auth"]
)
class CookieTokenRefreshView(APIView):


    def post(self, request):

        refresh_token = request.data.get("refresh")

        if not refresh_token:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        try:
            refresh = RefreshToken(refresh_token)
            access = str(refresh.access_token)

            response = Response({
                "message": "توکن رفرش شد",
                "refresh":str(refresh),
                "access":access
                })

            # response.set_cookie(
            #     "access",
            #     access,
            #     httponly=True,
            #     secure=True,
            #     samesite="Lax"
            # )

            # response.set_cookie(
            #     "refresh",
            #     refresh,
            #     httponly=True,
            #     secure=True,
            #     samesite="Lax"
            # )
            return response

        except Exception:
            return Response(status=status.HTTP_401_UNAUTHORIZED)