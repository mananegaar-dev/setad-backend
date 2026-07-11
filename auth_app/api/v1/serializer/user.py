  
from rest_framework import serializers
from auth_app.api.v1.serializer.area import AreaSerializer
from django.contrib.auth import get_user_model


class CurrentUserSerializer(serializers.ModelSerializer):
    groups = serializers.SerializerMethodField()
    role = serializers.SerializerMethodField()
    areas = AreaSerializer(many=True, read_only=True)

    class Meta:
        model = get_user_model()
        fields = [
            "id",
            "username",
            "first_name",
            "last_name",
            "groups",
            "areas",
            "role",
        ]

    def get_groups(self, obj):
        return list(obj.groups.values_list("name", flat=True))

    def get_role(self, obj):
        groups = list(obj.groups.values_list("name", flat=True))
        return groups[0] if groups else None
