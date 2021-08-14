from rest_framework import serializers
from taggit.serializers import TagListSerializerField

from accounts.models import User
from bases.serializers import ModelSerializer
from posts.models import EcoCarping


class EcoCarpingSerializer(ModelSerializer):
    tags = TagListSerializerField()
    created_at = serializers.SerializerMethodField()

    class Meta:
        model = EcoCarping
        fields = ['id', 'user', 'latitude', 'longitude',
                  'image', 'title', 'text', 'tags', 'created_at']

    def get_created_at(self, data):
        return data.created_at.strftime("%Y-%m-%d %H:%M")


class EcoRankingSerializer(ModelSerializer):
    image = serializers.SerializerMethodField()
    level = serializers.SerializerMethodField()
    eco_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'image', 'level', 'badge', 'eco_count']
        order_by = ['-eco_count']

    def get_image(self, data):
        return data.profile.get().image

    def get_level(self, data):
        return data.profile.get().level.level

    def get_eco_count(self, data):
        return data.eco.all().count()
