from rest_framework import serializers
from taggit.serializers import TagListSerializerField
from bases.serializers import ModelSerializer
from camps.models import CampSite, AutoCamp
from comments.serializers import ReviewSerializer


# class GetPopularSearchSerializer(serializers.Serializer):

class AutoCampSerializer(ModelSerializer):
    review = ReviewSerializer(many=True, read_only=True)
    tags = TagListSerializerField()
    review_count = serializers.SerializerMethodField()

    class Meta:
        model = AutoCamp
        fields = ['id', 'user', 'latitude', 'longitude', 'image',
                  'title', 'text', 'views', 'tags', 'review', 'review_count', 'bookmark']

    def get_review_count(self, data):
        return data.review.count()


class AutoCampMainSerializer(ModelSerializer):

    class Meta:
        model = AutoCamp
        fields = ['id', 'image']
