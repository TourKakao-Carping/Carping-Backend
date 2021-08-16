from rest_framework import serializers
from taggit.serializers import TagListSerializerField
from bases.serializers import ModelSerializer
from camps.models import CampSite, AutoCamp
from comments.serializers import ReviewSerializer, BookMarkSerializer


# class GetPopularSearchSerializer(serializers.Serializer):

class AutoCampSerializer(ModelSerializer):
    review = ReviewSerializer(many=True, read_only=True)
    bookmark = BookMarkSerializer(many=True, read_only=True)
    tags = TagListSerializerField()

    class Meta:
        model = AutoCamp
        fields = ['id', 'user', 'latitude', 'longitude', 'image',
                  'title', 'text', 'views', 'tags', 'review', 'bookmark']


class AutoCampMainSerializer(ModelSerializer):

    class Meta:
        model = AutoCamp
        fields = ['id', 'image']
