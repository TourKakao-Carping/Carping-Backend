from rest_framework import serializers

from accounts.models import User
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


class MyInfoSerializer(ModelSerializer):
    nickname = serializers.SerializerMethodField()
    bio = serializers.SerializerMethodField()
    interest = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'nickname', 'username', 'bio', 'interest', 'email']

    def get_nickname(self, data):
        return data.profile.get().nickname

    def get_bio(self, data):
        return data.profile.get().bio

    def get_interest(self, data):
        return data.profile.get().interest
