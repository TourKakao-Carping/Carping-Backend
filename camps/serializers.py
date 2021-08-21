from django.db.models import Avg
from rest_framework import serializers
from taggit.serializers import TagListSerializerField

from bases.serializers import ModelSerializer
from camps.models import CampSite, AutoCamp
from comments.models import Review
from comments.serializers import ReviewSerializer


# class GetPopularSearchSerializer(serializers.Serializer):

class AutoCampSerializer(ModelSerializer):
    review = ReviewSerializer(many=True, read_only=True)
    tags = TagListSerializerField()
    star1_avg = serializers.SerializerMethodField()
    star2_avg = serializers.SerializerMethodField()
    star3_avg = serializers.SerializerMethodField()
    star4_avg = serializers.SerializerMethodField()
    total_star_avg = serializers.SerializerMethodField()
    review_count = serializers.SerializerMethodField()
    check_bookmark = serializers.SerializerMethodField()

    class Meta:
        model = AutoCamp
        fields = ['id', 'user', 'latitude', 'longitude', 'image',
                  'title', 'text', 'views', 'tags', 'review', 'star1_avg',
                  'star2_avg', 'star3_avg', 'star4_avg', 'total_star_avg',
                  'review_count', 'check_bookmark']

    def get_star1_avg(self, data):
        return Review.objects.filter(autocamp=data).aggregate(Avg('star1'))['star1__avg']

    def get_star2_avg(self, data):
        return Review.objects.filter(autocamp=data).aggregate(Avg('star2'))['star2__avg']

    def get_star3_avg(self, data):
        return Review.objects.filter(autocamp=data).aggregate(Avg('star3'))['star3__avg']

    def get_star4_avg(self, data):
        return Review.objects.filter(autocamp=data).aggregate(Avg('star4'))['star4__avg']

    def get_total_star_avg(self, data):
        return Review.objects.filter(autocamp=data).aggregate(Avg('total_star'))['total_star__avg']

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


class MainPageThemeSerializer(ModelSerializer):
    class Meta:
        model = CampSite
        fields = ['id', 'image', 'type', 'address', 'name', 'phone', ]
