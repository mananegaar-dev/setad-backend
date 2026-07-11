
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from excel_app.models import Area


class AreaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Area
        fields = ["id", "name"]


class UserSerializer(serializers.ModelSerializer):

    areas = serializers.PrimaryKeyRelatedField(
        queryset=Area.objects.all(),
        many=True,
        write_only=True,
        required=False
    )

    areas_display = AreaSerializer(
        source="areas",
        many=True,
        read_only=True
    )

    role = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = get_user_model()
        fields = [
            "id",
            "username",
            "password",
            "phone_number",
            "first_name",
            "last_name",
            "areas",
            "areas_display",
            "role",
        ]
        extra_kwargs = {
            "password": {"write_only": True}
        }

    def create(self, validated_data):
        areas = validated_data.pop("areas", [])
        role_name = validated_data.pop("role", None)

        user = get_user_model().objects.create_user(**validated_data)

        if role_name:
            group, _ = Group.objects.get_or_create(name=role_name)
            user.groups.add(group)

        user.areas.set(areas)

        return user

    def update(self, instance, validated_data):
        areas = validated_data.pop("areas", None)
        role_name = validated_data.pop("role", None)

        password = validated_data.pop("password", None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if password:
            instance.set_password(password)

        instance.save()

        if areas is not None:
            instance.areas.set(areas)

        if role_name:
            group, _ = Group.objects.get_or_create(name=role_name)
            instance.groups.clear()
            instance.groups.add(group)

        return instance