from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema

from auth_app.models.activity import UserActivityLog
from excel_app.api.v1.serializer.logs import UserActivityLogSerializer , LastDocumentActivityLogSerializer

from rest_framework.response import Response
from rest_framework import status, generics
from django.shortcuts import get_object_or_404

from excel_app.models import Fields


@extend_schema(
    summary="لیست لاگ فعالیت کاربران",
    tags=["Logs"],
)
class UserActivityLogListView(ListAPIView):
    serializer_class = UserActivityLogSerializer
    permission_classes = [IsAuthenticated]

    def is_super_admin(self):
        return self.request.user.groups.filter(name="super_admin").exists()

    def get_queryset(self):
        user = self.request.user

        qs = (
            UserActivityLog.objects
            .select_related(
                "actor",
                "document",
                "document__sub_area",
                "document__sub_area__area",
            )
            .order_by("-created_at")
        )

        if self.is_super_admin():
            return qs

        return qs.filter(
            document__sub_area__area__in=user.areas.all()
        )




@extend_schema(
    summary="آخرین لاگ پرونده",
    tags=["Logs"],
)
class LastBoardOfTrusteeLogAPIView(generics.GenericAPIView):
    serializer_class = LastDocumentActivityLogSerializer

    def get(self, request, document_id):
        # Validate document exists
        get_object_or_404(Fields, id=document_id)

        # Query last log for board_of_trustees change
        log = (
            UserActivityLog.objects
            .filter(
                document_id_cache=document_id,
                message__icontains="هیئت امناء"
            )
            .select_related("actor")
            .order_by("-created_at")
            .first()
        )

        if not log:
            return Response(
                {"message": "هیچ لاگی برای هیئت امناء یافت نشد."},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = self.get_serializer(log)
        return Response(serializer.data, status=status.HTTP_200_OK)
