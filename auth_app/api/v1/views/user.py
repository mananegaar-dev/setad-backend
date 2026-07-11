from drf_spectacular.utils import extend_schema
from rest_framework.generics import ListAPIView
from auth_app.api.v1.serializer.user import CurrentUserSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

@extend_schema(
    summary="اطلاعات کاربر فعلی",
    tags=["Auth"]
)
class CurrentUserView(ListAPIView):
    permission_classes =[IsAuthenticated]
    pagination_class = None

    def get(self, request):
        serializer = CurrentUserSerializer(request.user)
        return Response(serializer.data)
