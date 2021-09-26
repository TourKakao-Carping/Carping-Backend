from rest_framework import serializers

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
    address = serializers.SerializerMethodField()

    class Meta:
        model = TourSite
        fields = ['id', 'image', 'lat', 'lon', 'name', 'distance', 'address']

    def get_distance(self, obj):
        data = self.context['request'].data

        lat = data.get('lat')
        lon = data.get('lon')

        distance = check_distance(float(lat), float(lon), obj.lat, obj.lon)

        return distance

    def get_address(self, obj):
        address = reverse_geocode(obj.lon, obj.lat)
        return address


class RegionCampSiteSerializer(ModelSerializer):
    distance = serializers.SerializerMethodField()
    bookmark_count = serializers.IntegerField()

    class Meta:
        model = CampSite
        ordering = ['distance']
        fields = ['id', 'image', 'type', 'address',
                  'name', 'phone', 'distance', 'bookmark_count']

    def get_distance(self, obj):
        data = self.context['request'].data

        lat = data.get('lat')
        lon = data.get('lon')

        distance = check_distance(float(lat), float(lon), obj.lat, obj.lon)

        return distance