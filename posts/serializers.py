from camps.models import AutoCamp
from rest_framework import serializers
from taggit.serializers import TagListSerializerField

from bases.serializers import ModelSerializer
from posts.models import EcoCarping, Post


class EcoCarpingSerializer(ModelSerializer):
    tags = TagListSerializerField()

    class Meta:
        model = EcoCarping
        fields = ['id', 'user', 'latitude', 'longitude',
                  'image', 'title', 'text', 'tags']


class AutoCampPostForWeekendSerializer(ModelSerializer):
    tags = TagListSerializerField()

    class Meta:
        model = Post
        fields = ['id', 'tags', 'title', 'thumbnail', 'views']


class AutoCampPostSerializer(ModelSerializer):
    tags = TagListSerializerField()

    class Meta:
        model = Post
        fields = '__all__'
