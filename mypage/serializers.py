from rest_framework import serializers

from accounts.models import User, EcoLevel, Profile
from accounts.serializers import EcoLevelSerializer
from bases.serializers import ModelSerializer
from bases.utils import check_distance
from camps.models import AutoCamp, CampSite
from camps.serializers import MainPageThemeSerializer
from posts.models import EcoCarping


class MyAutoCampSerializer(ModelSerializer):
    class Meta:
        model = AutoCamp
        fields = ['id', 'image1', 'title', 'total_star_avg', 'review_count']


class ScrapCampSiteSerializer(ModelSerializer):
    distance = serializers.SerializerMethodField()
    bookmark_count = serializers.SerializerMethodField()

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

    def get_bookmark_count(self, data):
        return data.bookmark.count()


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
    # scrap = serializers.BooleanField()
    # like = serializers.BooleanField()


# 프로필 페이지 - 이미지, 휴대폰 번호, 레벨, 배지이미지, 알람설정 -- 알람설정여부는 모델 추가 필요
class MyProfileSerializer(ModelSerializer):
    badge = serializers.SerializerMethodField()

    # alarm = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = ['id', 'image', 'phone', 'level', 'badge']  # alarm 추가 필요

    def get_level(self, data):
        if data.level is None:
            data.level = 1
        return data.level.level

    def get_badge(self, data):
        return EcoLevelSerializer(data.level, read_only=True).data['image']

    # def get_alarm(self, data):
    #     return data.certification.get().alarm


# 개인정보 페이지 - 닉네임, 이름, 한줄소개, 관심키워드, 이메일
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
