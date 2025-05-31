from typing import Optional

from rest_framework import serializers

from base.enum import EventStatus, EventType
from event.models import EventModel, EventContactPerson

class EventContactPersonSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventContactPerson
        exclude = [
            "is_active"
        ]

class EventCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventModel
        exclude = [
            "is_active",
            "status",
            "admin_comment"
        ]


class EventSerializer(serializers.ModelSerializer):
    deletion_time = serializers.SerializerMethodField(read_only=True)

    def get_deletion_time(self, obj) -> Optional[str]:
        return obj.deletion_time if hasattr(obj, "deletion_time") else None

    class Meta:
        model = EventModel
        fields = "__all__"


class EventDetailsSerializer(EventSerializer):
    contact_person = EventContactPersonSerializer(source="event_contact_person", many=True)
    deletion_time = serializers.SerializerMethodField(read_only=True)

    def get_deletion_time(self, obj) -> Optional[str]:
        return obj.deletion_time if hasattr(obj, "deletion_time") else None

    class Meta:
        model = EventModel
        fields = "__all__"

class EventUpdateAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventModel
        fields = [
            "status",
            "admin_comment"
        ]