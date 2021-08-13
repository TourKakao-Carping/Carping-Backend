from django.utils.translation import gettext_lazy as _
from rest_framework import serializers


class Serializer(serializers.Serializer):
    pass


class ModelSerializer(serializers.ModelSerializer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        create_only_fields = getattr(self.Meta, "create_only_fields", [])
        for field_name in create_only_fields:
            field = self.fields.get(field_name)
            field.read_only = self.instance is not None

    def create(self, validated_data):
        try:
            if hasattr(validated_data, "user") and self.context["request"].user:
                validated_data["user"] = self.context["request"].user
        except AttributeError:
            pass

        return self.Meta.model.objects.create(**validated_data)


class MessageSerializer(serializers.Serializer):
    message = serializers.CharField(read_only=True, help_text=_("Detailed response from server"))
