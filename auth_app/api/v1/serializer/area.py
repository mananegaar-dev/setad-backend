from rest_framework import serializers
from excel_app.models import Area, BoardOfTrustee, CertificateType, Neighborhood, SubArea

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
    class Meta:
        model = BoardOfTrustee
        fields = ["id", "name"]


class CertificateTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = CertificateType
        fields = ["id", "name"]
