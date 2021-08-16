from rest_framework import serializers
from taggit.serializers import TagListSerializerField
from bases.serializers import ModelSerializer
from camps.models import CampSite, AutoCamp


# class GetPopularSearchSerializer(serializers.Serializer):

class AutoCampSerializer(ModelSerializer):
    tags = TagListSerializerField()

    class Meta:
        model = AutoCamp
        fields = ['id', 'user', 'latitude', 'longitude', 'image', 'title', 'text', 'views', 'tags']


class AutoCampMainSerializer(ModelSerializer):

    class Meta:
        model = AutoCamp
        fields = ['id', 'image']
