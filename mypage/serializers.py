from rest_framework import serializers

from accounts.models import Profile
from accounts.serializers import EcoLevelSerializer
from bases.serializers import ModelSerializer
from bases.utils import check_distance
from camps.models import AutoCamp, CampSite
from posts.models import EcoCarping


class MyAutoCampSerializer(ModelSerializer):
    class Meta:
        model = AutoCamp
        fields = ['id', 'image1', 'title', 'total_star_avg', 'review_count']


class ScrapCampSiteSerializer(ModelSerializer):
    distance = serializers.SerializerMethodField()
    bookmark_count = serializers.IntegerField()

    class Meta:
        model = CampSite
        ordering = ['distance']
        fields = ['id', 'image', 'address',
                  'name', 'distance', 'bookmark_count']

    def get_distance(self, obj):
        data = self.context['request'].data

        lat = data.get('lat')
        lon = data.get('lon')

        distance = check_distance(float(lat), float(lon), obj.lat, obj.lon)
        return distance


class MyEcoSerializer(ModelSerializer):
    username = serializers.SerializerMethodField()
    created_at = serializers.SerializerMethodField()

    class Meta:
        model = EcoCarping
        fields = ['id', 'user', 'username', 'image1', 'title', 'text', 'created_at']

    def get_username(self, data):
        if type(data) == dict:
            return data['username']
        return data.user.username

    def get_created_at(self, data):
        return data.created_at.strftime("%Y-%m-%d %H:%M")


class MyPageSerializer(serializers.Serializer):
    sort = serializers.CharField()
    subsort = serializers.CharField()


class InfoSerializer(ModelSerializer):
    username = serializers.SerializerMethodField()
    email = serializers.SerializerMethodField()
    level = serializers.SerializerMethodField()
    badge = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = ['id', 'image', 'nickname', 'username', 'email', 'phone', 'level', 'badge', 'bio', 'interest']

    def get_username(self, data):
        return data.user.username

    def get_email(self, data):
        return data.user.email

    def get_level(self, data):
        if data.level is None:
            data.level = 1
        return data.level.level

    def get_badge(self, data):
        return EcoLevelSerializer(data.level, read_only=True).data['image']
