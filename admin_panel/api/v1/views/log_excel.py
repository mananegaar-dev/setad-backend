from rest_framework.views import APIView
from django.http import HttpResponse
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment

from auth_app.models.activity import UserActivityLog




from drf_spectacular.utils import extend_schema



@extend_schema(
    summary="خروجی اکسل از لاگ",
    tags=["panel-admin"],
)
class UserActivityLogExcelView(APIView):

    def get(self, request):

        logs = UserActivityLog.objects.select_related(
            "actor",
            "document"
        ).order_by("-created_at")

        document_id = request.GET.get("document_id")
        user_id = request.GET.get("user_id")
        start_date = request.GET.get("start_date")
        end_date = request.GET.get("end_date")

        if document_id:
            logs = logs.filter(document_id=document_id)

        if user_id:
            logs = logs.filter(actor_id=user_id)

        if start_date:
            logs = logs.filter(created_at__gte=start_date)

        if end_date:
            logs = logs.filter(created_at__lte=end_date)

        workbook = Workbook()
        sheet = workbook.active
        sheet.title = "Activity Logs"

        headers = [
            "Log ID",
            "Username",
            "User ID",
            "Action",
            "Document ID",
            "Message",
            "Created At",
        ]

        sheet.append(headers)

        for col in sheet[1]:
            col.font = Font(bold=True)
            col.alignment = Alignment(horizontal="center")

        for log in logs:

            sheet.append([
                log.id,
                log.actor.username if log.actor else "Unknown",
                log.actor.id if log.actor else None,
                log.action,
                log.document.id if log.document else None,
                log.message,
                str(log.created_at),
            ])

        for column in sheet.columns:
            max_length = 0
            column_letter = column[0].column_letter

            for cell in column:
                try:
                    if cell.value:
                        max_length = max(max_length, len(str(cell.value)))
                except:
                    pass

            sheet.column_dimensions[column_letter].width = max_length + 5

        response = HttpResponse(
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

        response["Content-Disposition"] = "attachment; filename=activity_logs.xlsx"

        workbook.save(response)

        return response
