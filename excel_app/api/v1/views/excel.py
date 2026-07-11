from datetime import date, datetime
import csv

import jdatetime
from django.db.models import Model
from django.http import HttpResponse
from django.utils.timezone import is_aware, make_naive, now
from drf_spectacular.utils import extend_schema
import openpyxl
from openpyxl.styles import Font
from openpyxl.cell import WriteOnlyCell

from excel_app.models import Fields
from excel_app.api.v1.views.search import UserSearchView

@extend_schema(
    summary="خروجی Excel از کاربران",
    tags=["کاربران"],
)
class FieldsExcelExportView(UserSearchView):
    CHUNK_SIZE = 2000
    AREA_FIELD_KEY = "__area_name"
    DB_ID_FIELD_KEY = "__db_id"
    EXCLUDED_FIELD_NAMES = {"id", "gender"}
    PRIORITY_FIELD_NAMES = (
        DB_ID_FIELD_KEY,
        AREA_FIELD_KEY,
        "sub_area",
        "neighborhood",
        "board_of_trustees",
        "first_name",
        "last_name",
        "father_name",
        "national_code",
    )

    def get_queryset(self):
        return super().get_queryset().select_related(
            "sub_area",
            "sub_area__area",
            "neighborhood",
            "board_of_trustees",
            "certificate_type",
            "last_edited_by",
        )
    @staticmethod
    def _normalize_excel_value(value):
        if value is None:
            return None

        if isinstance(value, jdatetime.datetime):
            return value.strftime("%Y/%m/%d %H:%M:%S")

        if isinstance(value, jdatetime.date):
            return value.strftime("%Y/%m/%d")

        if isinstance(value, datetime):
            if is_aware(value):
                value = make_naive(value)
            return jdatetime.datetime.fromgregorian(datetime=value).strftime("%Y/%m/%d %H:%M:%S")

        if isinstance(value, date):
            return jdatetime.date.fromgregorian(date=value).strftime("%Y/%m/%d")

        return value

    @staticmethod
    def _full_name_with_title(obj):
        first_name = (obj.first_name or "").strip()
        last_name = (obj.last_name or "").strip()
        base_name = f"{first_name} {last_name}".strip()

        if obj.gender == Fields.GenderType.MAN:
            return f"جناب آقای {base_name}".strip()
        if obj.gender == Fields.GenderType.WOMAN:
            return f"سرکار خانم {base_name}".strip()
        return base_name

    @staticmethod
    def _field_value(obj, field_name):
        if field_name == "sub_area":
            return obj.sub_area.name if obj.sub_area_id else None
        if field_name == "neighborhood":
            return obj.neighborhood.name if obj.neighborhood_id else None
        if field_name == "board_of_trustees":
            return obj.board_of_trustees.name if obj.board_of_trustees_id else None
        if field_name == "certificate_type":
            return obj.certificate_type.name if obj.certificate_type_id else None
        value = getattr(obj, field_name)
        if isinstance(value, Model):
            return str(value)
        return value

    @classmethod
    def _ordered_export_field_names(cls):
        all_field_names = [field.name for field in Fields._meta.fields]
        remaining = [
            name
            for name in all_field_names
            if name not in cls.PRIORITY_FIELD_NAMES and name not in cls.EXCLUDED_FIELD_NAMES
        ]
        return list(cls.PRIORITY_FIELD_NAMES) + remaining

    @classmethod
    def _header_title(cls, field_name, field_verbose_names):
        if field_name == cls.DB_ID_FIELD_KEY:
            return "شناسه"
        if field_name == cls.AREA_FIELD_KEY:
            return "منطقه"
        return field_verbose_names.get(field_name, field_name)

    @classmethod
    def _export_value(cls, obj, field_name):
        if field_name == cls.DB_ID_FIELD_KEY:
            return obj.id
        if field_name == cls.AREA_FIELD_KEY:
            return obj.sub_area.area.name if obj.sub_area_id else None
        return cls._field_value(obj, field_name)

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        wb = openpyxl.Workbook(write_only=True)
        ws = wb.create_sheet(title="Users")
        ws.title = "Users"

        export_fields = [field for field in Fields._meta.fields]
        field_verbose_names = {field.name: str(field.verbose_name) for field in export_fields}
        ordered_field_names = self._ordered_export_field_names()
        header_titles = ["ردیف"] + [
            self._header_title(field_name, field_verbose_names) for field_name in ordered_field_names
        ] + ["عنوان و نام کامل"]

        header_font = Font(bold=True)
        header_row = []
        for title in header_titles:
            cell = WriteOnlyCell(ws, value=title)
            cell.font = header_font
            header_row.append(cell)
        ws.append(header_row)

        for row_number, obj in enumerate(queryset.iterator(chunk_size=self.CHUNK_SIZE), start=1):
            row_values = [row_number] + [
                self._normalize_excel_value(self._export_value(obj, field_name))
                for field_name in ordered_field_names
            ]
            row_values.append(self._full_name_with_title(obj))
            ws.append(row_values)

        response = HttpResponse(
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        response["Content-Disposition"] = f'attachment; filename="{now()}.xlsx"'

        wb.save(response)
        return response


@extend_schema(
    summary="خروجی CSV از کاربران",
    tags=["کاربران"],
)
class ConvertToCsv(UserSearchView):
    CHUNK_SIZE = 5000

    def get_queryset(self):
        return super().get_queryset().select_related(
            "sub_area",
            "sub_area__area",
            "neighborhood",
            "board_of_trustees",
            "certificate_type",
            "last_edited_by",
        )
    @staticmethod
    def _normalize_excel_value(value):
        if value is None:
            return None

        if isinstance(value, jdatetime.datetime):
            return value.strftime("%Y/%m/%d %H:%M:%S")

        if isinstance(value, jdatetime.date):
            return value.strftime("%Y/%m/%d")

        if isinstance(value, datetime):
            if is_aware(value):
                value = make_naive(value)
            return jdatetime.datetime.fromgregorian(datetime=value).strftime("%Y/%m/%d %H:%M:%S")

        if isinstance(value, date):
            return jdatetime.date.fromgregorian(date=value).strftime("%Y/%m/%d")

        return value

    @staticmethod
    def _full_name_with_title(obj):
        first_name = (obj.first_name or "").strip()
        last_name = (obj.last_name or "").strip()
        base_name = f"{first_name} {last_name}".strip()

        if obj.gender == Fields.GenderType.MAN:
            return f"جناب آقای {base_name}".strip()
        if obj.gender == Fields.GenderType.WOMAN:
            return f"سرکار خانم {base_name}".strip()
        return base_name

    @staticmethod
    def _field_value(obj, field_name):
        if field_name == "sub_area":
            return obj.sub_area.name if obj.sub_area_id else None
        if field_name == "neighborhood":
            return obj.neighborhood.name if obj.neighborhood_id else None
        if field_name == "board_of_trustees":
            return obj.board_of_trustees.name if obj.board_of_trustees_id else None
        if field_name == "certificate_type":
            return obj.certificate_type.name if obj.certificate_type_id else None
        value = getattr(obj, field_name)
        if isinstance(value, Model):
            return str(value)
        return value

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        export_fields = [field for field in Fields._meta.fields]
        field_names = [field.name for field in export_fields]
        headers = [str(field.verbose_name) for field in export_fields] + ["منطقه", "عنوان و نام کامل"]
        filename = f'fields_{now().strftime("%Y%m%d_%H%M%S")}.csv'
        response = HttpResponse(content_type="text/csv; charset=utf-8")
        response["Content-Disposition"] = f'attachment; filename="{filename}"'
        # UTF-8 BOM helps Excel detect Persian text correctly.
        response.write("\ufeff")
        writer = csv.writer(response)
        writer.writerow(headers)

        for obj in queryset.iterator(chunk_size=self.CHUNK_SIZE):
            row_values = [
                self._normalize_excel_value(self._field_value(obj, field_name))
                for field_name in field_names
            ]
            row_values.append(obj.sub_area.area.name if obj.sub_area_id else "")
            row_values.append(self._full_name_with_title(obj))
            writer.writerow(row_values)
        return response


FieldsCsvExportView = ConvertToCsv
