from rest_framework import serializers
from taggit.serializers import TagListSerializerField

from bases.serializers import ModelSerializer
from posts.models import EcoCarping


class EcoCarpingSerializer(ModelSerializer):
    tags = TagListSerializerField()

    class Meta:
        model = EcoCarping
        fields = ['id', 'user', 'latitude', 'longitude', 'image', 'title', 'text', 'tags']
