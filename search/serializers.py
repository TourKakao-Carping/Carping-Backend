from rest_framework import serializers

from accounts.models import Search
from bases.serializers import ModelSerializer
from bases.utils import check_distance, reverse_geocode
from camps.models import TourSite, AutoCamp, CampSite


class AutoCampSearchSerializer(ModelSerializer):
    distance = serializers.SerializerMethodField()

    class Meta:
        model = AutoCamp
        fields = ['id', 'user', 'image1', 'latitude', 'longitude', 'title', 'text', 'distance']

    def get_distance(self, obj):
        data = self.context['request'].data

        lat = data.get('lat')
        lon = data.get('lon')

        distance = check_distance(float(lat), float(lon), obj.latitude, obj.longitude)

        return distance


class TourSiteSerializer(ModelSerializer):
    distance = serializers.SerializerMethodField()

    class Meta:
        model = TourSite
        fields = ['id', 'image', 'lat', 'lon', 'name', 'distance', 'address']

    def get_distance(self, obj):
        data = self.context['request'].data

        lat = data.get('lat')
        lon = data.get('lon')

        distance = check_distance(float(lat), float(lon), obj.lat, obj.lon)

        return distance


class RegionCampSiteSerializer(ModelSerializer):

    class Meta:
        model = CampSite
        fields = ['id', 'name']


class MainSearchSerializer(ModelSerializer):
    distance = serializers.SerializerMethodField()

    class Meta:
        model = CampSite
        ordering = ['distance']
        fields = ['id', 'name', 'address', 'distance']

    def get_distance(self, obj):
        data = self.context['request'].data

        lat = data.get('lat')
        lon = data.get('lon')

        distance = check_distance(float(lat), float(lon), obj.lat, obj.lon)

        return distance


class UserKeywordSerializer(ModelSerializer):

    class Meta:
        model = Search
        fields = ['keyword']
