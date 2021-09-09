from rest_framework import serializers
from taggit.serializers import TagListSerializerField, TaggitSerializer

from bases.serializers import ModelSerializer
from bases.utils import check_distance
from comments.serializers import CommentSerializer
from posts.models import EcoCarping, Post, Share
from camps.models import CampSite


class AutoCampPostForWeekendSerializer(TaggitSerializer, ModelSerializer):
    tags = TagListSerializerField()

    class Meta:
        model = Post
        fields = ['id', 'tags', 'title', 'thumbnail', 'views']


class EcoCarpingSerializer(TaggitSerializer, ModelSerializer):
    username = serializers.SerializerMethodField()
    profile = serializers.SerializerMethodField()
    comment = CommentSerializer(many=True, read_only=True)
    tags = TagListSerializerField()
    created_at = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()

    class Meta:
        model = EcoCarping
        fields = ['id', 'user', 'username', 'profile', 'latitude', 'longitude', 'place',
                  'image1', 'image2', 'image3', 'image4', 'title', 'text', 'trash',
                  'tags', 'created_at', 'comment', 'like_count', 'is_liked']

    def get_username(self, data):
        return data.user.username

    def get_profile(self, data):
        return data.user.profile.get().image

    def get_created_at(self, data):
        return data.created_at.strftime("%Y-%m-%d %H:%M")

    def get_is_liked(self, data):
        # if data.like.count() == 0:
        #     return 0
        if self.context['request'].user.eco_like.filter(id=data.id):
            return True
        return False


class EcoCarpingSortSerializer(TaggitSerializer, ModelSerializer):
    username = serializers.SerializerMethodField()

    class Meta:
        model = EcoCarping
        fields = ['id', 'user', 'username', 'image1', 'title', 'text', 'created_at']

    def get_username(self, data):
        if type(data) == dict:
            return data['username']
        return data.user.username


class AutoCampPostSerializer(TaggitSerializer, ModelSerializer):
    tags = TagListSerializerField()

    class Meta:
        model = Post
        fields = '__all__'

    def to_representation(self, instance):
        re_ret = {}

        count = 0
        ret = super().to_representation(instance)
        re_ret["id"] = ret.pop("id")
        re_ret["created_at"] = ret.pop("created_at")
        re_ret["updated_at"] = ret.pop("updated_at")
        re_ret["title"] = ret.pop("title")
        re_ret["thumbnail"] = ret.pop("thumbnail")
        re_ret["views"] = ret.pop("views")
        re_ret["tags"] = ret.pop("tags")

        for i in range(3):
            camp = {}
            camp["text"] = ret[f"text{i+1}"]
            camp["image"] = ret[f"image{i+1}"]
            camp["source"] = ret[f"source{i+1}"]
            campsite_pk = ret[f"campsite{i+1}"]
            camp["sub_title"] = ret[f"sub_title{i+1}"]

            if campsite_pk is not None:
                campsite = CampSite.objects.get(id=campsite_pk)
                camp["name"] = campsite.name
                camp["address"] = campsite.address
                camp["phone"] = campsite.phone
                camp["type"] = campsite.type
                camp["oper_day"] = campsite.oper_day
                camp["website"] = campsite.website
                camp["sub_facility"] = campsite.sub_facility
                count += 1
            else:
                camp["address"] = ""
                camp["phone"] = ""
                camp["type"] = ""
                camp["oper_day"] = ""
                camp["website"] = ""
                camp["sub_facility"] = ""

            re_ret[f"campsite{i+1}"] = camp

        re_ret["count"] = count
        return re_ret


class PostLikeSerializer(serializers.Serializer):
    post_to_like = serializers.IntegerField(write_only=True)


# 무료나눔
class ShareSerializer(TaggitSerializer, ModelSerializer):
    username = serializers.SerializerMethodField()
    profile = serializers.SerializerMethodField()
    region = serializers.SerializerMethodField()
    comment = CommentSerializer(many=True, read_only=True)
    tags = TagListSerializerField()
    created_at = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()

    class Meta:
        model = Share
        fields = ['id', 'user', 'username', 'profile', 'region',
                  'image1', 'image2', 'image3', 'image4', 'title', 'text', 'tags',
                  'chat_addr', 'created_at', 'comment', 'like_count', 'is_liked']

    def get_username(self, data):
        return data.user.username

    def get_profile(self, data):
        return data.user.profile.get().image

    def get_region(self, data):
        return data.region.name

    def get_created_at(self, data):
        return data.created_at.strftime("%Y-%m-%d %H:%M")

    def get_is_liked(self, data):
        if self.context['request'].user.eco_like.filter(id=data.id):
            return True
        return False


class ShareSortSerializer(TaggitSerializer, ModelSerializer):
    like_count = serializers.IntegerField()
    distance = serializers.SerializerMethodField()

    class Meta:
        model = Share
        fields = ['id', 'is_shared', 'image1', 'title',
                  'text', 'created_at', 'like_count', 'distance']
        # distance 반환은 하지만 안드에서 사용하지는 않을 것, 거리순 정렬용

    def get_distance(self, obj):
        data = self.context['request'].data

        lat = data.get('latitude')
        lon = data.get('longitude')

        distance = check_distance(float(lat), float(lon), obj.region.latitude, obj.region.longitude)
        return distance


class ShareCompleteSerializer(serializers.Serializer):
    share_to_complete = serializers.IntegerField(write_only=True)
