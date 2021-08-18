from rest_framework import serializers
from taggit.serializers import TagListSerializerField

from bases.serializers import ModelSerializer
from camps.models import CampSite, AutoCamp
from comments.serializers import ReviewSerializer


# class GetPopularSearchSerializer(serializers.Serializer):

class AutoCampSerializer(ModelSerializer):
    review = ReviewSerializer(many=True, read_only=True)
    tags = TagListSerializerField()
    review_count = serializers.SerializerMethodField()
    check_bookmark = serializers.SerializerMethodField()

    class Meta:
        model = AutoCamp
        fields = ['id', 'user', 'latitude', 'longitude', 'image',
                  'title', 'text', 'views', 'tags', 'review', 'review_count', 'check_bookmark']

    def get_review_count(self, data):
        return data.review.count()

    def get_check_bookmark(self, data):
        # 스웨거 테스트 시에는 self.context['request'].user 가 익명일 수 있으니 User.objects.get(id=~)로 바꾸고 할 것
        if data.bookmark.count() == 0:
            return 0
        if self.context['request'].user.autocamp_bookmark.filter(id=data.id):
            return 1
        return 0


class AutoCampMainSerializer(ModelSerializer):

    class Meta:
        model = AutoCamp
        fields = ['id', 'image']
