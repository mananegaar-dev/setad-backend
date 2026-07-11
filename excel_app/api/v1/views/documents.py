# django-rest-framework
from rest_framework.generics import ListAPIView
from rest_framework.viewsets import ModelViewSet

# models
from auth_app.models.activity import UserActivityLog
from excel_app.models import Fields

# serializer
from excel_app.api.v1.serializer.documents import (
    DocumentSerializer,
    UpdateDocumentSerializer,
)

# docs
from drf_spectacular.utils import extend_schema

# permission
from permission import AreaAccessPermission


from rest_framework.exceptions import MethodNotAllowed
    

@extend_schema(
    responses={200: DocumentSerializer(many=True)},
    summary="لیست سندها",
    tags=["docs"],
)
class DocumentView(ListAPIView):
    serializer_class = DocumentSerializer
    queryset = Fields.objects.order_by("-id")
    permission_classes = [AreaAccessPermission]

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user

        if not user.is_authenticated:
            return qs.none()

        if user.groups.filter(name="super_admin").exists():
            return qs

        return qs.filter(sub_area__area__in=user.areas.all())


@extend_schema(
    request=UpdateDocumentSerializer,
    summary="مدیریت سندها",
    tags=["docs"],
)
class UpdateDocumentView(ModelViewSet):

    permission_classes = [AreaAccessPermission]
    serializer_class = UpdateDocumentSerializer

    queryset = Fields.objects.select_related(
        "sub_area",
        "sub_area__area",
        "neighborhood",
        "board_of_trustees",
    ).order_by("-id")

    http_method_names = ["get", "put", "patch", "post",]

    # ----------------------------------------
    # utilities
    # ----------------------------------------

    @property
    def is_super_admin(self):
        return self.request.user.groups.filter(name="super_admin").exists()

    def _get_field_label(self, instance, field):
        try:
            return instance._meta.get_field(field).verbose_name
        except Exception:
            return field

    def _get_actor_name(self):
        user = self.request.user
        if not user.is_authenticated:
            return "ناشناس"

        full_name = user.get_full_name().strip()
        return full_name or user.username

    def _log_activity(self, action, message, document=None):

        user = self.request.user if self.request.user.is_authenticated else None

        UserActivityLog.objects.create(
            actor=user,
            actor_id_cache=user.id if user else None,
            action=action,
            document=document,
            document_id_cache=document.id if document else None,
            message=message,
        )

    def _format_changes(self, instance, validated_data):

        changes = []

        for field, new_value in validated_data.items():

            old_value = getattr(instance, field, None)

            if str(old_value) == str(new_value):
                continue

            field_label = self._get_field_label(instance, field)

            changes.append(
                f"{field_label} از < {old_value} > به < {new_value} > تغییر کرد"
            )

        return "، ".join(changes)

    # ----------------------------------------
    # queryset security
    # ----------------------------------------

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user

        if not user.is_authenticated:
            return qs.none()

        if self.is_super_admin:
            return qs

        return qs.filter(
            sub_area__area__in=user.areas.all()
        )

    # ----------------------------------------
    # actions
    # ----------------------------------------

    def retrieve(self, request, *args, **kwargs):

        instance = self.get_object()

        self._log_activity(
            action="retrieve",
            message=f"کاربر {self._get_actor_name()} جزئیات مستند با شناسه {instance.id} را مشاهده کرد.",
            document=instance,
        )

        return super().retrieve(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        kwargs["partial"] = True
        return super().update(request, *args, **kwargs)

    # ----------------------------------------
    # CRUD hooks
    # ----------------------------------------

    def perform_update(self, serializer):

        user = self.request.user
        instance = self.get_object()

        changes_text = self._format_changes(instance, serializer.validated_data)

        serializer.save(last_edited_by=user)

        if changes_text:
            message = (
                f"کاربر {user.username} "
                f"مستند با شناسه {instance.id} را ویرایش کرد. "
                f"{changes_text}."
            )

            self._log_activity(
                action="update",
                message=message,
                document=instance,
            )

    def perform_create(self, serializer):

        user = self.request.user
        instance = serializer.save(last_edited_by=user)

        filled_fields = []

        for field, value in serializer.validated_data.items():

            field_label = self._get_field_label(instance, field)

            filled_fields.append(
                f"{field_label} = < {value} >"
            )

        message = (
            f"کاربر {user.username} "
            f"مستند با شناسه {instance.id} را ایجاد کرد. "
            f"اطلاعات ثبت شده: {', '.join(filled_fields)}"
        )

        self._log_activity(
            action="create",
            message=message,
            document=instance,
        )

    def perform_destroy(self, instance):

        user = self.request.user

        message = (
            f"کاربر {user.username} "
            f"مستند با شناسه {instance.id} را حذف کرد."
        )

        self._log_activity(
            action="delete",
            message=message,
            document=instance,
        )

        super().perform_destroy(instance)


    def list(self, request, *args, **kwargs):
        raise MethodNotAllowed("GET")