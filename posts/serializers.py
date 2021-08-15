from rest_framework import serializers
from taggit.serializers import TagListSerializerField

from bases.serializers import ModelSerializer
from posts.models import EcoCarping, Post


class AutoCampPostForWeekendSerializer(ModelSerializer):
    tags = TagListSerializerField()

    class Meta:
        model = Post
        fields = ['id', 'tags', 'title', 'thumbnail', 'views']


class EcoCarpingSerializer(ModelSerializer):
    tags = TagListSerializerField()
    created_at = serializers.SerializerMethodField()

    class Meta:
        model = EcoCarping
        fields = ['id', 'user', 'latitude', 'longitude',
                  'image', 'title', 'text', 'tags', 'created_at']

    def get_created_at(self, data):
        return data.created_at.strftime("%Y-%m-%d %H:%M")


class AutoCampPostSerializer(ModelSerializer):
    tags = TagListSerializerField()

    class Meta:
        model = Post
        fields = '__all__'
