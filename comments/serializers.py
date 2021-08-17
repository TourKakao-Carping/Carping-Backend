from rest_framework import serializers

from accounts.models import User
from bases.serializers import ModelSerializer
from comments.models import Comment, Review


class ReviewSerializer(ModelSerializer):
    like_count = serializers.SerializerMethodField()
    check_like = serializers.SerializerMethodField()

    class Meta:
        model = Review
        fields = ['id', 'user', 'text', 'image', 'star1', 'star2',
                  'star3', 'star4', 'total_star', 'like_count', 'check_like']

    def get_like_count(self, data):
        return data.like.count()

    def get_check_like(self, data):
        # 스웨거 테스트 시에는 self.context['request'].user 가 익명일 수 있으니 User.objects.get(id=~)로 바꾸고 할 것
        if data.like.count() == 0:
            return 0
        for i in range(len(data.like.through.objects.all())):
            return 1 if self.context['request'].user == data.like.through.objects.all()[i].user else 0


class CommentSerializer(ModelSerializer):
    like_count = serializers.SerializerMethodField()
    check_like = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ['id', 'user', 'text', 'root', 'like_count', 'check_like']

    def get_like_count(self, data):
        return data.like.count()

    def get_check_like(self, data):
        # 스웨거 테스트 시에는 self.context['request'].user 가 익명일 수 있으니 User.objects.get(id=~)로 바꾸고 할 것
        if data.like.count() == 0:
            return 0
        for i in range(len(data.like.through.objects.all())):
            return 1 if self.context['request'].user == data.like.through.objects.all()[i].user else 0

