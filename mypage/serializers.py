from rest_framework import serializers

from accounts.models import User, EcoLevel, Profile
from accounts.serializers import EcoLevelSerializer
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
