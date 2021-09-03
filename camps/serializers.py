from bases.utils import check_distance

from django.db.models import Avg
from rest_framework import serializers
from taggit.serializers import TagListSerializerField, TaggitSerializer

from bases.serializers import ModelSerializer
from camps.models import CampSite, AutoCamp
from comments.models import Review
from comments.serializers import ReviewSerializer


# class GetPopularSearchSerializer(serializers.Serializer):

class AutoCampSerializer(TaggitSerializer, ModelSerializer):
    review = ReviewSerializer(many=True, read_only=True)
    tags = TagListSerializerField()
    my_star_avg = serializers.SerializerMethodField()
    my_review_count = serializers.SerializerMethodField()
    check_bookmark = serializers.SerializerMethodField()

    class Meta:
        model = AutoCamp
        fields = ['id', 'user', 'latitude', 'longitude', 'image1', 'image2', 'image3', 'image4',
                  'title', 'text', 'views', 'tags', 'review', 'star1_avg',
                  'star2_avg', 'star3_avg', 'star4_avg', 'my_star_avg', 'total_star_avg',
                  'my_review_count', 'review_count', 'check_bookmark']

    def get_my_star_avg(self, data):
        if not Review.objects.filter(user=self.context['request'].user, autocamp=data):
            return 0
        else:
            return round(Review.objects.filter(user=self.context['request'].user, autocamp=data).aggregate(
                Avg('total_star'))['total_star__avg'], 1)

    def get_my_review_count(self, data):
        return data.review.filter(user=self.context['request'].user).count()

    def get_check_bookmark(self, data):
        # if data.bookmark.count() == 0:
        #     return 0
        if self.context['request'].user.autocamp_bookmark.filter(id=data.id):
            return 1
        return 0


class AutoCampMainSerializer(ModelSerializer):

    class Meta:
        model = AutoCamp
        fields = ['id', 'image1']


class AutoCampBookMarkSerializer(serializers.Serializer):
    autocamp_to_bookmark = serializers.IntegerField(write_only=True)


class CampSiteBookMarkSerializer(serializers.Serializer):
    campsite_to_bookmark = serializers.IntegerField(write_only=True)


class MainPageThemeSerializer(serializers.Serializer):
    theme = serializers.CharField()
    sort = serializers.CharField()
    select = serializers.CharField()
    lat = serializers.FloatField()
    lon = serializers.FloatField()
    # distance = serializers.SerializerMethodField()
    #
    # class Meta:
    #     model = CampSite
    #     fields = ['id', 'image', 'type', 'address',
    #               'name', 'phone', 'distance', ]
    #
    # def get_distance(self, data):
    #     distance = data.get('distance')
    #     distance_km = f"{distance}km"
    #     return distance_km


class CampSiteSerializer(ModelSerializer):
    bookmark_count = serializers.SerializerMethodField()
    check_bookmark = serializers.SerializerMethodField()
    # distance = serializers.SerializerMethodField()

    class Meta:
        model = CampSite
        fields = ['id', 'image', 'type', 'address', 'name', 'phone', 'bookmark_count', 'check_bookmark']

    def get_bookmark_count(self, data):
        return data.bookmark.count()

    def get_check_bookmark(self, data):
        if data.bookmark.count() == 0:
            return 0
        if self.context['request'].user.campsite_bookmark.filter(id=data.id):
            return 1
        return 0

    # def get_distance(self, data):
    #     distance = data.get('distance')
    #     distance_km = f"{distance}km"
    #     return distance_km
