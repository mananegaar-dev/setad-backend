from rest_framework.generics import ListAPIView

from excel_app.models import Fields, Neighborhood, SubArea

from django.contrib.auth import get_user_model


from django.db.models import Count, Q
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import get_user_model
from drf_spectacular.utils import extend_schema

@extend_schema(
    summary="اطلاعات آماری",
    tags=["panel-admin"],
)
class StatsView(APIView):

    def get(self, request):

        fields_stats = Fields.objects.aggregate(
            total=Count("id"),
            active=Count("id", filter=Q(status=Fields.StatusType.ACTIVE)),
            inactive=Count("id", filter=Q(status=Fields.StatusType.INACTIVE)),
            reserve=Count("id", filter=Q(status=Fields.StatusType.RESERVATION)),
            pending=Count("id", filter=Q(status=Fields.StatusType.PENDING)),
        )

        data = {
            "fields": fields_stats,
            "neighborhood_count": Neighborhood.objects.count(),
            "sub_area_count": SubArea.objects.count(),
            "user_count": get_user_model().objects.count(),
        }

        return Response(data)