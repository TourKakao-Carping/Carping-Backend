from rest_framework import serializers

from accounts.models import User
from bases.serializers import ModelSerializer
from comments.models import Comment, Review


class ReviewSerializer(ModelSerializer):
    created_at = serializers.SerializerMethodField()
    like_count = serializers.SerializerMethodField()
    check_like = serializers.SerializerMethodField()

    class Meta:
        model = Review
        fields = ['id', 'user', 'text', 'image', 'star1', 'star2',
                  'star3', 'star4', 'total_star', 'created_at', 'like_count', 'check_like']

    def get_created_at(self, data):
        return data.created_at.strftime("%Y. %m. %d")

    def get_like_count(self, data):
        return data.like.count()

    def get_check_like(self, data):
        print(self.context['request'].user)
        # 스웨거 테스트 시에는 self.context['request'].user 가 익명일 수 있으니 User.objects.get(id=~)로 바꾸고 할 것
        if data.like.count() == 0:
            return 0
        for i in range(len(data.like.through.objects.all())):
            if data.like.through.objects.all()[i].user == self.context['request'].user:
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
        for i in range(len(data.like.through.objects.all())):
            if data.like.through.objects.all()[i].user == self.context['request'].user:
                return 1
        return 0

