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
    is_bookmarked = serializers.SerializerMethodField()

    class Meta:
        model = AutoCamp
        fields = ['id', 'user', 'latitude', 'longitude', 'image1', 'image2', 'image3', 'image4',
                  'title', 'text', 'views', 'tags', 'review', 'star1_avg',
                  'star2_avg', 'star3_avg', 'star4_avg', 'my_star_avg', 'total_star_avg',
                  'my_review_count', 'review_count', 'is_bookmarked']

    def get_my_star_avg(self, data):
        if not Review.objects.filter(user=self.context['request'].user, autocamp=data):
            return 0
        else:
            return round(Review.objects.filter(user=self.context['request'].user, autocamp=data).aggregate(
                Avg('total_star'))['total_star__avg'], 1)

    def get_my_review_count(self, data):
        return data.review.filter(user=self.context['request'].user).count()

    def get_is_bookmarked(self, data):
        # if data.bookmark.count() == 0:
        #     return 0
        if self.context['request'].user.autocamp_bookmark.filter(id=data.id):
            return True
        return False


class AutoCampMainSerializer(ModelSerializer):

    class Meta:
        model = AutoCamp
        fields = ['id', 'image1']


class AutoCampBookMarkSerializer(serializers.Serializer):
    autocamp_to_bookmark = serializers.IntegerField(write_only=True)


class CampSiteBookMarkSerializer(serializers.Serializer):
    campsite_to_bookmark = serializers.IntegerField(write_only=True)


class MainPageThemeSerializer(ModelSerializer):
    distance = serializers.SerializerMethodField()
    bookmark_count = serializers.IntegerField()
    is_bookmarked = serializers.BooleanField()

    class Meta:
        model = CampSite
        ordering = ['distance']
        fields = ['id', 'image', 'type', 'address',
                  'name', 'phone', 'distance', 'bookmark_count', 'is_bookmarked']

    def get_distance(self, obj):
        data = self.context['request'].data

        lat = data.get('lat')
        lon = data.get('lon')

        distance = check_distance(float(lat), float(lon), obj.lat, obj.lon)

        return distance


class CampSiteSerializer(ModelSerializer):
    tags = TagListSerializerField()
    bookmark_count = serializers.IntegerField()
    is_bookmarked = serializers.BooleanField()
    distance = serializers.SerializerMethodField()

    class Meta:
        model = CampSite
        fields = ['id', 'image', 'type', 'address', 'name',
                  'phone', 'distance', 'lat', 'lon', 'address',
                  'oper_day', 'season', 'phone', 'faculty', 'permission_date',
                  'sub_facility', 'rental_items', 'animal', 'brazier', 'tags',
                  'bookmark_count', 'is_bookmarked']

    def get_distance(self, obj):
        data = self.context['request'].data

        lat = data.get('lat')
        lon = data.get('lon')

        distance = check_distance(float(lat), float(lon), obj.lat, obj.lon)

        return distance
