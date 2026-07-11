from rest_framework import serializers
from excel_app.models import (
    Area,
    BoardOfTrustee,
    BoardOfTrusteeCategory,
    CertificateType,
    Neighborhood,
    SubArea,
)

class AreaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Area
        fields = ["id", "name"]



class SubAreaSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubArea
        fields = ["id", "name"]


class NeighborhoodSerializer(serializers.ModelSerializer):
    class Meta:
        model = Neighborhood
        fields = ["id", "name"]


class BoardOfTrusteeSerializer(serializers.ModelSerializer):
    category = serializers.SerializerMethodField()

    class Meta:
        model = BoardOfTrustee
        fields = ["id", "name", "category"]

    def get_category(self, obj):
        category = obj.board_of_Trustee_category
        if not category:
            return None
        return {"id": category.id, "name": category.name}


class BoardOfTrusteeCategorySerializer(serializers.ModelSerializer):
    items = BoardOfTrusteeSerializer(source="board_of_Trustee_category", many=True)

    class Meta:
        model = BoardOfTrusteeCategory
        fields = ["id", "name", "items"]


class CertificateTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = CertificateType
        fields = ["id", "name"]
