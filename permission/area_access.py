class AreaAccessMixin:
    area_lookup = "sub_area__area"

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user

        if not user.is_authenticated:
            return queryset.none()

        if user.groups.filter(name="super_admin").exists():
            return queryset

        user_areas = user.areas.values_list("id", flat=True)

        if not user_areas:
            return queryset.none()

        return queryset.filter(**{
            f"{self.area_lookup}__id__in": user_areas
        })


from rest_framework.permissions import BasePermission, SAFE_METHODS


class AreaAccessPermission(BasePermission):
  

    area_lookup = "sub_area__area"

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        user = request.user

        if user.groups.filter(name="super_admin").exists():
            return True

        user_area_ids = user.areas.values_list("id", flat=True)

        if not user_area_ids:
            return False

        try:
            area_attr = self.area_lookup.split("__")
            area_instance = obj
            for attr in area_attr:
                area_instance = getattr(area_instance, attr)
                if area_instance is None:
                    return False
        except AttributeError:
            return False

        return area_instance.id in user_area_ids
