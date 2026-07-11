from rest_framework.viewsets import ModelViewSet
from django.contrib.auth import get_user_model
from admin_panel.api.v1.serializer.users import UserSerializer
from rest_framework.filters import SearchFilter
from drf_spectacular.utils import extend_schema

from auth_app.models.activity import UserActivityLog
from permission import SuperAdmin

User = get_user_model()


@extend_schema(
    summary="مدیریت کاربران",
    tags=["panel-admin"],
)
class UserView(ModelViewSet):

    permission_classes = [SuperAdmin]

    queryset = User.objects.exclude(groups__name="super_admin")

    serializer_class = UserSerializer

    filter_backends = [SearchFilter]
    search_fields = ["username", "phone_number", "first_name", "last_name"]

    http_method_names = ["get", "post", "put", "patch", "delete"]

    # ----------------------------------------
    # utilities
    # ----------------------------------------

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

    def _log_activity(self, action, message):

        actor = self.request.user if self.request.user.is_authenticated else None

        UserActivityLog.objects.create(
            actor=actor,
            actor_id_cache=actor.id if actor else None,
            action=action,
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
    # actions
    # ----------------------------------------

    def retrieve(self, request, *args, **kwargs):

        instance = self.get_object()

        self._log_activity(
            action="retrieve",
            message=f"کاربر {self._get_actor_name()} اطلاعات کاربر با شناسه {instance.id} را مشاهده کرد.",
        )

        return super().retrieve(request, *args, **kwargs)

    # ----------------------------------------
    # CRUD hooks
    # ----------------------------------------

    def perform_create(self, serializer):

        actor = self.request.user
        instance = serializer.save()

        filled_fields = []

        for field, value in serializer.validated_data.items():

            field_label = self._get_field_label(instance, field)

            filled_fields.append(
                f"{field_label} = < {value} >"
            )

        message = (
            f"کاربر {actor.username} "
            f"یک کاربر جدید با شناسه {instance.id} ایجاد کرد. "
            f"اطلاعات ثبت شده: {', '.join(filled_fields)}"
        )

        self._log_activity(
            action="create",
            message=message,
        )

    def perform_update(self, serializer):

        actor = self.request.user
        instance = self.get_object()

        changes_text = self._format_changes(instance, serializer.validated_data)

        serializer.save()

        if changes_text:

            message = (
                f"کاربر {actor.username} "
                f"کاربر با شناسه {instance.id} را ویرایش کرد. "
                f"{changes_text}."
            )

            self._log_activity(
                action="update",
                message=message,
            )

    def perform_destroy(self, instance):

        actor = self.request.user

        message = (
            f"کاربر {actor.username} "
            f"کاربر با شناسه {instance.id} را حذف کرد."
        )

        self._log_activity(
            action="delete",
            message=message,
        )

        super().perform_destroy(instance)

