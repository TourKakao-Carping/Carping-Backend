from rest_framework import serializers

from bases.serializers import ModelSerializer
from camps.models import AutoCamp, CampSite


class MyAutoCampSerializer(ModelSerializer):

    class Meta:
        model = AutoCamp
        fields = ['id', 'latitude', 'longitude', 'image1', 'title', 'total_star_avg', 'review_count']


class ScrapCampSiteSerializer(ModelSerializer):
    bookmark_count = serializers.SerializerMethodField()

    class Meta:
        model = CampSite
        fields = ['id', 'lat', 'lon', 'image', 'name', 'bookmark_count']

    def get_bookmark_count(self, data):
        return data.bookmark.count()


class MyPageSerializer(serializers.Serializer):
    sort = serializers.CharField()
    scrap = serializers.BooleanField()
    like = serializers.BooleanField()
