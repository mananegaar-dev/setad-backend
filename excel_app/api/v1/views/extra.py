from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework.response import Response
from rest_framework.generics import ListAPIView
from rest_framework.views import APIView

from excel_app.api.v1.serializer.area import (
    BoardOfTrusteeSerializer,
    BoardOfTrusteeCategorySerializer,
    CertificateTypeSerializer,
    NeighborhoodSerializer,
    SubAreaSerializer,
)
from excel_app.models import (
    BoardOfTrustee,
    BoardOfTrusteeCategory,
    CertificateType,
    Neighborhood,
    SubArea,
)

from permission.area_access import AreaAccessMixin

@extend_schema(
    summary="لیست انواع مدرک تحصیلی",
    tags=["Meta"],
)
class CertificateTypeListView(ListAPIView):
    serializer_class = CertificateTypeSerializer
    pagination_class = None
    queryset = CertificateType.objects.all().order_by("name")


@extend_schema(
    summary="لیست ناحیه‌ها",
    tags=["Meta"],
    parameters=[
        OpenApiParameter(name="area", type=int, location=OpenApiParameter.QUERY, required=False),
    ],
)
class SubAreaListView(ListAPIView):
    serializer_class = SubAreaSerializer
    pagination_class = None

    def get_queryset(self):
        queryset = SubArea.objects.select_related("area").all().order_by("name")
        area_id = self.request.query_params.get("area")
        if area_id:
            queryset = queryset.filter(area_id=area_id)
        return queryset


@extend_schema(
    summary="لیست محله‌ها",
    tags=["Meta"],
    parameters=[
        OpenApiParameter(name="sub_area", type=int, location=OpenApiParameter.QUERY, required=False),
    ],
)
class NeighborhoodListView(AreaAccessMixin, ListAPIView):
    serializer_class = NeighborhoodSerializer
    pagination_class = None
    queryset = Neighborhood.objects.select_related(
        "sub_area", "sub_area__area"
    ).all().order_by("name")

    area_lookup = "sub_area__area"

    def get_queryset(self):
        queryset = super().get_queryset()

        sub_area_id = self.request.query_params.get("sub_area")
        if sub_area_id:
            queryset = queryset.filter(sub_area_id=sub_area_id)

        return queryset



@extend_schema(
    summary="لیست هیئت امنا",
    tags=["Meta"],
)
class BoardOfTrusteeListView(ListAPIView):
    serializer_class = BoardOfTrusteeSerializer
    pagination_class = None

    def get_queryset(self):
        return BoardOfTrustee.objects.select_related("board_of_Trustee_category").all().order_by("name")


@extend_schema(
    summary="لیست هیئت امنا بر اساس دسته‌بندی",
    tags=["Meta"],
)
class BoardOfTrusteeGroupedListView(APIView):
    pagination_class = None

    def get(self, request):
        categories = BoardOfTrusteeCategory.objects.prefetch_related("board_of_Trustee_category").all().order_by("name")
        category_data = BoardOfTrusteeCategorySerializer(categories, many=True).data

        uncategorized = BoardOfTrustee.objects.select_related("board_of_Trustee_category").filter(
            board_of_Trustee_category__isnull=True
        ).order_by("name")

        return Response(
            {
                "categories": category_data,
                "uncategorized": BoardOfTrusteeSerializer(uncategorized, many=True).data,
            }
        )
