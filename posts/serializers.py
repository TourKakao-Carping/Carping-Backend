import datetime

from rest_framework import serializers
from taggit.serializers import TagListSerializerField, TaggitSerializer

from bases.serializers import ModelSerializer
from bases.utils import check_distance, modify_created_time
from comments.serializers import CommentSerializer
from posts.models import EcoCarping, Post, Share, Region, Store, UserPostInfo
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
        return data.user.profile.get().image.url

    def get_created_at(self, data):
        return modify_created_time(data)

    def get_is_liked(self, data):
        # if data.like.count() == 0:
        #     return 0
        if self.context['request'].user.eco_like.filter(id=data.id):
            return True
        return False


class EcoCarpingSortSerializer(TaggitSerializer, ModelSerializer):
    username = serializers.SerializerMethodField()
    created_at = serializers.SerializerMethodField()

    class Meta:
        model = EcoCarping
        fields = ['id', 'user', 'username',
                  'image1', 'title', 'text', 'created_at']

    def get_username(self, data):
        if type(data) == dict:
            return data['username']
        return data.user.username

    def get_created_at(self, data):
        return modify_created_time(data)


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


# 동네 검색
class SigunguSearchSerializer(ModelSerializer):

    class Meta:
        model = Region
        fields = ['sido', 'sigungu']


class DongSearchSerializer(ModelSerializer):

    class Meta:
        model = Region
        fields = ['id', 'sido', 'sigungu', 'dong']


# 무료나눔
class ShareSerializer(TaggitSerializer, ModelSerializer):
    username = serializers.SerializerMethodField()
    profile = serializers.SerializerMethodField()
    region = serializers.SerializerMethodField()
    comment = CommentSerializer(many=True, read_only=True)
    tags = TagListSerializerField()
    created_at = serializers.SerializerMethodField()
    like_count = serializers.IntegerField()
    is_liked = serializers.BooleanField()

    class Meta:
        model = Share
        fields = ['id', 'user', 'username', 'profile', 'region', 'is_shared',
                  'image1', 'image2', 'image3', 'image4', 'title', 'text', 'tags',
                  'chat_addr', 'created_at', 'comment', 'like_count', 'is_liked']

    def get_username(self, data):
        return data.user.username

    def get_profile(self, data):
        return data.user.profile.get().image.url

    def get_region(self, data):
        return data.region.dong

    def get_created_at(self, data):
        return modify_created_time(data)


class SharePostSerializer(TaggitSerializer, ModelSerializer):
    tags = TagListSerializerField()

    class Meta:
        model = Share
        fields = ['id', 'user', 'region', 'image1', 'image2',
                  'image3', 'image4', 'title', 'text', 'tags',
                  'chat_addr']


class ShareSortSerializer(TaggitSerializer, ModelSerializer):
    region = serializers.SerializerMethodField()
    like_count = serializers.IntegerField()
    created_at = serializers.SerializerMethodField()

    class Meta:
        model = Share
        fields = ['id', 'region', 'is_shared', 'image1', 'title',
                  'text', 'created_at', 'like_count']

    def get_region(self, data):
        return data.region.dong

    def get_created_at(self, data):
        return modify_created_time(data)


class ShareCompleteSerializer(serializers.Serializer):
    share_to_complete = serializers.IntegerField(write_only=True)


class StoreSerializer(ModelSerializer):
    class Meta:
        model = Store
        fields = ['id', 'item', 'image', 'price']


class UserPostAtoZSerializer(serializers.ModelSerializer):
    thumbnail = serializers.SerializerMethodField()
    title = serializers.SerializerMethodField()
    is_liked = serializers.BooleanField(read_only=True)

    class Meta:
        # id, thumnail, title, review, is_liked
        model = UserPostInfo
        fields = ['id', 'title', 'total_star_avg',
                  'thumbnail', 'is_liked']

    def get_thumbnail(self, instance):
        request = self.context.get('request')
        thumnail = instance.user_post.thumbnail

        return request.build_absolute_uri(thumnail.url)

    def get_title(self, instance):
        title = instance.user_post.title
        return title
