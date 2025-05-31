from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()

class NestedCreateSerializerMixin:
    def create(self, validated_data):
        removable_fields = []
        for field in self._writable_fields:
            if isinstance(field, serializers.BaseSerializer):
                removable_fields.append(field)
                field.is_valid()
                field.save()
        for f in removable_fields:
            self._writable_fields.pop(f.name)
        return super().create(validated_data)


class UserBasicInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "first_name", "last_name", "email", "phone", "image", "role", "position"]