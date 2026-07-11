from rest_framework import serializers

from auth_app.models.activity import UserActivityLog


class UserActivityLogSerializer(serializers.ModelSerializer):
    actor_name = serializers.SerializerMethodField()

    class Meta:
        model = UserActivityLog
        fields = ["id", "actor", "actor_name", "action", "message", "created_at"]

    def get_actor_name(self, obj):
        if not obj.actor:
            return "ناشناس"
        full_name = obj.actor.get_full_name().strip()
        return full_name or obj.actor.username




class LastDocumentActivityLogSerializer(serializers.ModelSerializer):
    actor_username = serializers.CharField(source="actor.username", read_only=True)

    class Meta:
        model = UserActivityLog
        fields = [
            "id",
            "actor_username",
            "action",
            "message",
            "created_at",
            "document_id",
        ]