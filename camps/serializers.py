from bases.utils import check_distance

from django.db.models import Avg
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from taggit.serializers import TagListSerializerField, TaggitSerializer

from bases.serializers import ModelSerializer
from camps.models import CampSite, AutoCamp
from comments.models import Review
from comments.serializers import ReviewSerializer


# class GetPopularSearchSerializer(serializers.Serializer):

class AutoCampSerializer(TaggitSerializer, ModelSerializer):
    review = ReviewSerializer(many=True, read_only=True)
    tags = TagListSerializerField()
    star1_avg = serializers.SerializerMethodField()
    star2_avg = serializers.SerializerMethodField()
    star3_avg = serializers.SerializerMethodField()
    star4_avg = serializers.SerializerMethodField()
    my_star_avg = serializers.SerializerMethodField()
    total_star_avg = serializers.SerializerMethodField()
    my_review_count = serializers.SerializerMethodField()
    review_count = serializers.SerializerMethodField()
    check_bookmark = serializers.SerializerMethodField()

    class Meta:
        model = AutoCamp
        fields = ['id', 'user', 'latitude', 'longitude', 'image',
                  'title', 'text', 'views', 'tags', 'review', 'star1_avg',
                  'star2_avg', 'star3_avg', 'star4_avg', 'my_star_avg', 'total_star_avg',
                  'my_review_count', 'review_count', 'check_bookmark']

    def get_star1_avg(self, data):
        return round(Review.objects.filter(autocamp=data).aggregate(Avg('star1'))['star1__avg'], 1)

    def get_star2_avg(self, data):
        return round(Review.objects.filter(autocamp=data).aggregate(Avg('star2'))['star2__avg'], 1)

    def get_star3_avg(self, data):
        return round(Review.objects.filter(autocamp=data).aggregate(Avg('star3'))['star3__avg'], 1)

    def get_star4_avg(self, data):
        return round(Review.objects.filter(autocamp=data).aggregate(Avg('star4'))['star4__avg'], 1)

    def get_my_star_avg(self, data):
        return round(Review.objects.filter(user=self.context['request'].user, autocamp=data).aggregate(
            Avg('total_star'))['total_star__avg'], 1)

    def get_total_star_avg(self, data):
        return round(Review.objects.filter(autocamp=data).aggregate(Avg('total_star'))['total_star__avg'], 1)

    def get_my_review_count(self, data):
        return data.review.filter(user=self.context['request'].user).count()

    def get_review_count(self, data):
        return data.review.count()

    def get_check_bookmark(self, data):
        if data.bookmark.count() == 0:
            return 0
        if self.context['request'].user.autocamp_bookmark.filter(id=data.id):
            return 1
        return 0


class AutoCampMainSerializer(ModelSerializer):

    class Meta:
        model = AutoCamp
        fields = ['id', 'image']


class AutoCampBookMarkSerializer(serializers.Serializer):
    autocamp_to_bookmark = serializers.IntegerField(write_only=True)


class MainPageThemeSerializer(ModelSerializer):
    distance = serializers.SerializerMethodField()
    # distance =

    class Meta:
        model = CampSite
        fields = ['id', 'image', 'type', 'address',
                  'name', 'phone', 'brazier', 'distance']

    def get_distance(self, data):
        distance = data.get('distance')
        distance_km = f"{distance}km"
        return distance_km
