from django.db.models import Q
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import generics

from excel_app.api.v1.serializer.documents import UpdateDocumentSerializer
from excel_app.models import Fields
from permission.area_access import AreaAccessMixin


@extend_schema(
    summary="جست‌وجوی سریع کاربران",
    description=(
        "جست‌وجوی سبک و سریع روی فیلدهای اصلی مدل Fields.\n\n"
        "فیلدهای فعال در جست‌وجو:\n"
        "- first_name\n"
        "- last_name\n"
        "- national_code\n"
        "- phone_number\n"
        "- neighborhood\n"
        "- status\n"
        "- birth_certificate_number\n\n"
        "- board_of_trustees\n\n"
        "- board_of_trustee_category\n\n"
        "نمونه‌ها:\n"
        "- q=علی\n"
        "- q=علی 0912\n"
        "- q=فعال 1234567890\n"
        "- gender=مرد\n"
        "- is_verified=true\n"
        "- area=2\n"
        "- sub_area=5\n"
        "- neighborhood=تهرانپارس\n"
        "- board_of_trustee_category=معتمدین\n"
    ),
    tags=["کاربران"],
    parameters=[
        OpenApiParameter(name="q", type=str, location=OpenApiParameter.QUERY),
        OpenApiParameter(name="full_name", type=str, location=OpenApiParameter.QUERY),
        OpenApiParameter(name="first_name", type=str, location=OpenApiParameter.QUERY),
        OpenApiParameter(name="last_name", type=str, location=OpenApiParameter.QUERY),
        OpenApiParameter(name="status", type=str, location=OpenApiParameter.QUERY),
        OpenApiParameter(name="national_code", type=str, location=OpenApiParameter.QUERY),
        OpenApiParameter(name="is_verified", type=bool, location=OpenApiParameter.QUERY),
        OpenApiParameter(name="area", type=int, location=OpenApiParameter.QUERY),
        OpenApiParameter(name="area_name", type=str, location=OpenApiParameter.QUERY),
        OpenApiParameter(name="sub_area", type=int, location=OpenApiParameter.QUERY),
        OpenApiParameter(name="sub_area_name", type=str, location=OpenApiParameter.QUERY),
        OpenApiParameter(name="neighborhood", type=str, location=OpenApiParameter.QUERY),
        OpenApiParameter(name="neighborhood_id", type=int, location=OpenApiParameter.QUERY),
        OpenApiParameter(name="board_of_trustees", type=str, location=OpenApiParameter.QUERY),
        OpenApiParameter(name="board_of_trustees_id", type=int, location=OpenApiParameter.QUERY),
        OpenApiParameter(name="board_of_trustee_category", type=str, location=OpenApiParameter.QUERY),
        OpenApiParameter(name="board_of_trustee_category_id", type=int, location=OpenApiParameter.QUERY),
        OpenApiParameter(name="gender", type=str, location=OpenApiParameter.QUERY),
    ],
)
class UserSearchView(AreaAccessMixin, generics.ListAPIView):
    serializer_class = UpdateDocumentSerializer
    area_lookup = "sub_area__area"

    DIGIT_TRANSLATION_TABLE = str.maketrans("۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩", "01234567890123456789")

    SEARCH_FIELDS = (
        "first_name",
        "last_name",
        "national_code",
        "phone_number",
        "sub_area__area__name",
        "sub_area__name",
        "neighborhood__name",
        "status",
        "birth_certificate_number",
        "board_of_trustees__name",
        "board_of_trustees__board_of_Trustee_category__name",
        "gender",
    )


    @classmethod
    def _normalize_digits(cls, value):
        if value is None:
            return ""
        return str(value).translate(cls.DIGIT_TRANSLATION_TABLE).strip()

    def _parse_int_param(self, value):
        normalized = self._normalize_digits(value)
        if not normalized:
            return None
        try:
            return int(normalized)
        except (TypeError, ValueError):
            return None

    def _build_q_filter(self, query):
        words = [word.strip() for word in query.split() if word.strip()]
        if not words:
            return Q()

        combined = Q()
        for word in words:
            per_word = Q()
            for field_name in self.SEARCH_FIELDS:
                per_word |= Q(**{f"{field_name}__icontains": word})
            int_word = self._parse_int_param(word)
            if int_word is not None:
                per_word |= Q(id=int_word)
                per_word |= Q(sub_area__area_id=int_word)
                per_word |= Q(sub_area_id=int_word)
                per_word |= Q(neighborhood_id=int_word)
            combined &= per_word
        return combined

    def _build_full_name_filter(self, full_name):
        words = [word.strip() for word in full_name.split() if word.strip()]
        if not words:
            return Q()

        combined = Q()
        for word in words:
            combined &= Q(first_name__icontains=word) | Q(last_name__icontains=word)
        return combined

    def _parse_bool_param(self, value):
        if value is None:
            return None
        normalized = str(value).strip().lower()
        if normalized in {"1", "true", "yes", "y"}:
            return True
        if normalized in {"0", "false", "no", "n"}:
            return False
        return None

    def get_queryset(self):
        params = self.request.query_params

        qs = Fields.objects.select_related(
            "sub_area",
            "sub_area__area",
            "board_of_trustees",
            "board_of_trustees__board_of_Trustee_category",
        )

        query = params.get("q", "").strip()
        if query:
            qs = qs.filter(self._build_q_filter(query))

        full_name = params.get("full_name", "").strip()
        if full_name:
            qs = qs.filter(self._build_full_name_filter(full_name))

        first_name = params.get("first_name", "").strip()
        if first_name:
            qs = qs.filter(first_name__icontains=first_name)

        last_name = params.get("last_name", "").strip()
        if last_name:
            qs = qs.filter(last_name__icontains=last_name)

        status_param = params.get("status")
        if status_param:
            statuses = [s.strip() for s in status_param.split(",")]
            qs = qs.filter(status__in=statuses)

        national_code = params.get("national_code", "").strip()
        if national_code:
            qs = qs.filter(national_code__icontains=national_code)

        is_verified = self._parse_bool_param(params.get("is_verified"))
        if is_verified is not None:
            qs = qs.filter(is_verified=is_verified)

        area_id = self._parse_int_param(params.get("area"))
        if area_id is not None:
            qs = qs.filter(sub_area__area_id=area_id)
        area_name = params.get("area_name", "").strip()
        if area_name:
            qs = qs.filter(sub_area__area__name__icontains=area_name)

        sub_area_id = self._parse_int_param(params.get("sub_area"))
        if sub_area_id is not None:
            qs = qs.filter(sub_area_id=sub_area_id)
        sub_area_name = params.get("sub_area_name", "").strip()
        if sub_area_name:
            qs = qs.filter(sub_area__name__icontains=sub_area_name)

        neighborhood = params.get("neighborhood")
        if neighborhood:
            qs = qs.filter(neighborhood__name__icontains=neighborhood)
        neighborhood_id = self._parse_int_param(params.get("neighborhood_id"))
        if neighborhood_id is not None:
            qs = qs.filter(neighborhood_id=neighborhood_id)

        board_of_trustees = params.get("board_of_trustees", "").strip()
        if board_of_trustees:
            qs = qs.filter(board_of_trustees__name__icontains=board_of_trustees)
        board_of_trustees_id = self._parse_int_param(params.get("board_of_trustees_id"))
        if board_of_trustees_id is not None:
            qs = qs.filter(board_of_trustees_id=board_of_trustees_id)

        board_of_trustee_category = params.get("board_of_trustee_category", "").strip()
        if board_of_trustee_category:
            qs = qs.filter(
                board_of_trustees__board_of_Trustee_category__name__icontains=board_of_trustee_category
            )
        board_of_trustee_category_id = self._parse_int_param(params.get("board_of_trustee_category_id"))
        if board_of_trustee_category_id is not None:
            qs = qs.filter(
                board_of_trustees__board_of_Trustee_category_id=board_of_trustee_category_id
            )

        gender = params.get("gender")
        if gender:
            qs = qs.filter(gender=gender.strip())

        return qs.order_by("-id").distinct()
