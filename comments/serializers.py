from rest_framework import serializers

from accounts.serializers import EcoLevelSerializer
from bases.serializers import ModelSerializer
from comments.models import Comment, Review


class ReviewSerializer(ModelSerializer):
    username = serializers.SerializerMethodField()
    profile = serializers.SerializerMethodField()
    created_at = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()

    class Meta:
        model = Review
        fields = ['id', 'user', 'username', 'profile', 'text', 'image', 'star1', 'star2',
                  'star3', 'star4', 'total_star', 'created_at', 'like_count', 'is_liked']

    def get_username(self, data):
        return data.user.username

    def get_profile(self, data):
        return data.user.profile.get().image

    def get_created_at(self, data):
        return data.created_at.strftime("%Y. %m. %d")

    def get_is_liked(self, data):
        # if data.like_count == 0:
        #     return 0
        if data.like.filter(id=self.context['request'].user.id):
            return True
        return False


class CommentSerializer(ModelSerializer):
    username = serializers.SerializerMethodField()
    profile = serializers.SerializerMethodField()
    level = serializers.SerializerMethodField()
    badge = serializers.SerializerMethodField()
    created_at = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ['id', 'user', 'username', 'profile', 'level',
                  'badge', 'text', 'root', 'created_at']

    def get_username(self, data):
        return data.user.username

    def get_profile(self, data):
        return data.user.profile.get().image

    def get_level(self, data):
        return data.user.profile.get().level.level

    def get_badge(self, data):
        return EcoLevelSerializer(data.user.profile.get().level, read_only=True).data['image']

    def get_created_at(self, data):
        return data.created_at.strftime("%Y-%m-%d %H:%M")


class ReviewLikeSerializer(serializers.Serializer):
    review_to_like = serializers.IntegerField(write_only=True)


class CommentLikeSerializer(serializers.Serializer):
    comment_to_like = serializers.IntegerField(write_only=True)
