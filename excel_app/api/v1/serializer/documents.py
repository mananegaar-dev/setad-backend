from typing import Optional

from rest_framework import serializers
from excel_app.models import Fields

from excel_app.api.v1.serializer.area import (
    AreaSerializer,
    BoardOfTrusteeSerializer,
    CertificateTypeSerializer,
    NeighborhoodSerializer,
    SubAreaSerializer,
)

class DocumentSerializer(serializers.ModelSerializer):

    area = AreaSerializer(source="sub_area.area", read_only=True)
    sub_area = SubAreaSerializer(read_only=True)
    neighborhood = NeighborhoodSerializer(read_only=True)
    board_of_trustees = BoardOfTrusteeSerializer(read_only=True)
    certificate_type = CertificateTypeSerializer(read_only=True)
    edit_time = serializers.DateTimeField(format="%Y/%m/%d %H:%M")
    class Meta:
        model = Fields
        fields = [
            "id",
            "area",
            "sub_area",
            "first_name",
            "last_name",
            "father_name",
            "birth_date",
            "neighborhood",
            "phone_number",
            "national_code",
            "board_of_trustees",
            "certificate_type",
            "status",
            "edit_time",
            "last_edited_by",
            "is_verified"   
            ]
        
class UpdateDocumentSerializer(serializers.ModelSerializer):
    edit_time = serializers.DateTimeField(format="%Y/%m/%d %H:%M", read_only=True)
    user_edit_time_name = serializers.SerializerMethodField()
    activity_logs = serializers.StringRelatedField(many=True, read_only=True)

    class Meta:
        model = Fields
        fields = '__all__'

    def get_user_edit_time_name(self, obj) -> Optional[str]:
        if not obj.last_edited_by:
            return None
        full_name = obj.last_edited_by.get_full_name().strip()
        return full_name or obj.last_edited_by.username

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["sub_area"] = SubAreaSerializer(instance.sub_area).data if instance.sub_area_id else None
        data["neighborhood"] = NeighborhoodSerializer(instance.neighborhood).data if instance.neighborhood_id else None
        data["board_of_trustees"] = (
            BoardOfTrusteeSerializer(instance.board_of_trustees).data
            if instance.board_of_trustees_id
            else None
        )
        data["certificate_type"] = (
            CertificateTypeSerializer(instance.certificate_type).data
            if instance.certificate_type_id
            else None
        )
        data["area"] = AreaSerializer(instance.sub_area.area).data if instance.sub_area_id else None
        return data
