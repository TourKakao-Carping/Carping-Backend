from bases.s3 import S3Client
from camps.constants import CAMP_TYPE
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
        if self.context['request'].user.autocamp_bookmark.filter(id=data.id):
            return True
        return False

    def validate(self, attrs):
        return super().validate(attrs)

    def update(self, instance, validated_data):
        """
        기존에 저장되어 있다면 이미지 삭제하고 다시 업로드
        """
        fields = validated_data.keys()

        s3 = S3Client()

        for key in fields:
            if key == "image1":
                if not instance.image1 == "" and not instance.image1 == None:
                    s3.delete_file(str(instance.image1))
            elif key == "image2":
                if not instance.image2 == "" and not instance.image2 == None:
                    s3.delete_file(str(instance.image2))
            elif key == "image3":
                if not instance.image3 == "" and not instance.image3 == None:
                    s3.delete_file(str(instance.image3))
            elif key == "image4":
                if not instance.image4 == "" and not instance.image4 == None:
                    s3.delete_file(str(instance.image4))
            else:
                pass
        return super().update(instance, validated_data)


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
    main_facility = serializers.SerializerMethodField()

    class Meta:
        model = CampSite
        fields = ['id', 'image', 'type', 'address', 'name',
                  'phone', 'distance', 'lat', 'lon', 'address',
                  'website', 'reservation', 'oper_day', 'season', 'phone', 'faculty',
                  'permission_date', 'main_facility', 'sub_facility', 'rental_item',
                  'animal', 'brazier', 'tags', 'bookmark_count', 'is_bookmarked']

    def get_distance(self, obj):
        data = self.context['request'].data

        lat = data.get('lat')
        lon = data.get('lon')

        distance = check_distance(float(lat), float(lon), obj.lat, obj.lon)

        return distance

    def get_main_facility(self, obj):
        # type = obj.type
        # type_arr = type.split(',')

        # for i in type_arr:
        #     if i == CAMP_TYPE[0]:
        main_facility = ""
        is_after = False
        if obj.main_autocamp > 0:
            main_facility += f"{CAMP_TYPE[0]}({obj.main_autocamp}개)"
            is_after = True

        if obj.main_general > 0:
            if is_after:
                main_facility += ", "

            main_facility += f"{CAMP_TYPE[1]}({obj.main_general}개)"
            is_after = True

        if obj.main_glamcamp > 0:
            if is_after:
                main_facility += ", "

            main_facility += f"{CAMP_TYPE[2]}({obj.main_glamcamp}개)"
            is_after = True

        if obj.main_caravan > 0:
            if is_after:
                main_facility += ", "

            main_facility += f"{CAMP_TYPE[3]}({obj.main_caravan}개)"
            is_after = True

        if obj.main_personal_caravan > 0:
            if is_after:
                main_facility += ", "

            main_facility += f"{CAMP_TYPE[4]}({obj.main_personal_caravan}개)"
            is_after = True

        if obj.toilet > 0:
            if is_after:
                main_facility += ", "

            main_facility += f"{CAMP_TYPE[5]}({obj.toilet}개)"

        if obj.shower > 0:
            if is_after:
                main_facility += ", "

            main_facility += f"{CAMP_TYPE[6]}({obj.shower}개)"

        return main_facility
