from accounts.models import Profile
from django.db.models.aggregates import Avg
from django.http import request
from comments.models import Review
import datetime

from rest_framework import serializers
from taggit.serializers import TagListSerializerField, TaggitSerializer

from bases.serializers import ModelSerializer
from bases.utils import check_distance, modify_created_time
from bases.s3 import S3Client

from comments.serializers import CommentSerializer, ReviewSerializer
from posts.models import EcoCarping, Post, Share, Region, Store, UserPost, UserPostInfo
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
            else:
                if not instance.image4 == "" and not instance.image4 == None:
                    s3.delete_file(str(instance.image4))

        return super().update(instance, validated_data)


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


class UserPostListSerializer(serializers.ModelSerializer):
    thumbnail = serializers.SerializerMethodField()
    title = serializers.SerializerMethodField()
    is_liked = serializers.BooleanField(read_only=True)
    author = serializers.SerializerMethodField()

    class Meta:
        # id, thumnail, title, review, is_liked
        model = UserPostInfo
        fields = ['id', 'title', 'total_star_avg', 'author',
                  'thumbnail', 'is_liked', 'category', 'pay_type', 'point']

    def get_author(self, instance):
        return instance.author.username

    def get_thumbnail(self, instance):
        request = self.context.get('request')
        thumnail = instance.user_post.thumbnail

        return request.build_absolute_uri(thumnail.url)

    def get_title(self, instance):
        title = instance.user_post.title
        return title


class UserPostAddProfileSerializer(UserPostListSerializer):
    user_profile = serializers.SerializerMethodField()

    class Meta:
        model = UserPostInfo
        fields = ['id', 'title', 'total_star_avg', 'author',
                  'thumbnail', 'is_liked', 'category', 'pay_type', 'point', 'user_profile']

    def get_user_profile(self, instance):
        request = self.context.get('request')
        profile = instance.author.profile.get()

        image = profile.image
        return request.build_absolute_uri(image.url)


class UserPostInfoDetailSerializer(serializers.ModelSerializer):
    userpost_id = serializers.SerializerMethodField()

    thumbnail = serializers.SerializerMethodField()
    author_name = serializers.SerializerMethodField()
    author_profile = serializers.SerializerMethodField()
    author_comment = serializers.SerializerMethodField()

    login_user = serializers.SerializerMethodField()
    login_user_profile = serializers.SerializerMethodField()

    title = serializers.CharField(read_only=True)
    review = ReviewSerializer(many=True, read_only=True)
    is_liked = serializers.BooleanField(read_only=True)

    my_star_avg = serializers.SerializerMethodField()
    my_review_count = serializers.SerializerMethodField()

    preview_image1 = serializers.SerializerMethodField()
    preview_image2 = serializers.SerializerMethodField()
    preview_image3 = serializers.SerializerMethodField()

    contents_count = serializers.SerializerMethodField()

    class Meta:
        model = UserPostInfo
        fields = ['id', 'userpost_id', 'author_name', 'author_profile', 'author_comment', 'title', 'thumbnail', 'point', 'info', 'recommend_to', 'is_liked', 'preview_image1', 'preview_image2', 'preview_image3', 'contents_count', 'like_count',  'kakao_openchat_url', 'star1_avg',
                  'star2_avg', 'star3_avg', 'star4_avg', 'my_star_avg', 'total_star_avg', 'my_review_count', 'review_count', 'login_user', 'login_user_profile', 'review']

    def get_userpost_id(self, instance):
        return instance.user_post.id

    def get_thumbnail(self, instance):
        request = self.context.get('request')
        thumnail = instance.user_post.thumbnail

        return request.build_absolute_uri(thumnail.url)

    def get_author_name(self, instance):
        return instance.author.username

    def get_author_profile(self, instance):
        request = self.context.get('request')
        profile = instance.author.profile.get()

        image = profile.image
        return request.build_absolute_uri(image.url)

    def get_author_comment(self, instance):
        profile = instance.author.profile.get()

        return profile.author_comment

    def get_login_user(self, instance):
        request = self.context.get('request')
        user = request.user

        return user.username

    def get_login_user_profile(self, instance):
        request = self.context.get('request')
        user = request.user

        profile = user.profile.get()

        image = profile.image
        return request.build_absolute_uri(image.url)

    def get_my_star_avg(self, instance):
        if not Review.objects.filter(user=self.context['request'].user, userpostinfo=instance):
            return 0
        else:
            return round(Review.objects.filter(user=self.context['request'].user, userpostinfo=instance).aggregate(
                Avg('total_star'))['total_star__avg'], 1)

    def get_my_review_count(self, instance):
        return instance.review.filter(user=self.context['request'].user).count()

    def get_preview_image1(self, instance):
        userpost = instance.user_post

        image1 = userpost.image1
        if not image1 == None and not image1 == "":
            request = self.context.get('request')
            return request.build_absolute_uri(image1.url)
        else:
            return None

    def get_preview_image2(self, instance):
        userpost = instance.user_post

        image2 = userpost.image2
        if not image2 == None and not image2 == "":
            request = self.context.get('request')
            return request.build_absolute_uri(image2.url)
        else:
            return None

    def get_preview_image3(self, instance):
        userpost = instance.user_post

        image3 = userpost.image3
        if not image3 == None and not image3 == "":
            request = self.context.get('request')
            return request.build_absolute_uri(image3.url)
        else:
            return None

    def get_contents_count(self, instance):
        userpost = instance.user_post

        if userpost.sub_title2 == None:
            return 1
        elif userpost.sub_title3 == None:
            return 2
        elif userpost.sub_title4 == None:
            return 3
        elif userpost.sub_title5 == None:
            return 4
        else:
            return 5

    # def


class OtherUserPostSerializer(serializers.ModelSerializer):
    pay_type = serializers.SerializerMethodField()

    class Meta:
        model = UserPost
        fields = ['id', 'title', 'thumbnail', 'pay_type']

    def get_pay_type(self, instance):
        return instance.userpostinfo_set.get().pay_type


class UserPostDetailSerializer(serializers.ModelSerializer):
    created_at = serializers.SerializerMethodField()
    author_name = serializers.SerializerMethodField()
    author_profile = serializers.SerializerMethodField()
    author_comment = serializers.SerializerMethodField()
    other_post = serializers.SerializerMethodField()

    class Meta:
        model = UserPost
        fields = ['id', 'created_at', 'author_name', 'author_profile',
                  'author_comment', 'title', 'thumbnail',
                  'sub_title1', 'text1', 'image1',
                  'sub_title2', 'text2', 'image2',
                  'sub_title3', 'text3', 'image3',
                  'sub_title4', 'text4', 'image4',
                  'sub_title5', 'text5', 'image5',
                  'other_post']

    def get_created_at(self, data):
        return data.created_at.strftime('%Y. %m. %d')

    def get_author_name(self, instance):
        return instance.userpostinfo_set.get().author.username

    def get_author_profile(self, instance):
        return instance.userpostinfo_set.get().author.profile.get().image.url

    def get_author_comment(self, instance):
        return instance.userpostinfo_set.get().author.profile.get().author_comment

    def get_other_post(self, instance):
        recent_post = instance.userpostinfo_set.get(
        ).author.user_post.latest('id').user_post
        return OtherUserPostSerializer(recent_post).data


class UserPostMoreReviewSerializer(serializers.ModelSerializer):
    review = ReviewSerializer(many=True, read_only=True)

    class Meta:
        model = UserPost
        fields = ['review']


class UserPostCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserPost
        fields = ['id', 'title', 'thumbnail',
                  'sub_title1', 'text1', 'image1',
                  'sub_title2', 'text2', 'image2',
                  'sub_title3', 'text3', 'image3',
                  'sub_title4', 'text4', 'image4',
                  'sub_title5', 'text5', 'image5']
