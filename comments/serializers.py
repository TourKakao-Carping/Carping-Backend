from rest_framework import serializers

from bases.serializers import ModelSerializer
from comments.models import Comment, Review


class ReviewSerializer(ModelSerializer):
    username = serializers.SerializerMethodField()
    created_at = serializers.SerializerMethodField()
    like_count = serializers.SerializerMethodField()
    check_like = serializers.SerializerMethodField()

    class Meta:
        model = Review
        fields = ['id', 'user', 'username', 'text', 'image', 'star1', 'star2',
                  'star3', 'star4', 'total_star', 'created_at', 'like_count', 'check_like']

    def get_username(self, data):
        return data.user.username

    def get_created_at(self, data):
        return data.created_at.strftime("%Y. %m. %d")

    def get_like_count(self, data):
        return data.like.count()

    def get_check_like(self, data):
        if data.like.count() == 0:
            return 0
        if data.like.filter(id=self.context['request'].user.id):
            return 1
        return 0


class CommentSerializer(ModelSerializer):
    created_at = serializers.SerializerMethodField()
    like_count = serializers.SerializerMethodField()
    check_like = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ['id', 'user', 'text', 'root', 'created_at', 'like_count', 'check_like']

    def get_created_at(self, data):
        return data.created_at.strftime("%Y-%m-%d %H:%M")

    def get_like_count(self, data):
        return data.like.count()

    def get_check_like(self, data):
        # 스웨거 테스트 시에는 self.context['request'].user 가 익명일 수 있으니 User.objects.get(id=~)로 바꾸고 할 것
        if data.like.count() == 0:
            return 0
        if data.like.filter(id=self.context['request'].user.id):
            return 1
        return 0

