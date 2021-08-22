from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken

from accounts.models import User, EcoLevel
from bases.serializers import ModelSerializer


class CustomTokenRefreshSerializer(serializers.Serializer):
    refresh_token = serializers.CharField()
    access_token = serializers.ReadOnlyField()

    def validate(self, attrs):
        refresh = RefreshToken(attrs['refresh_token'])

        data = {'access_token': str(refresh.access_token)}
        return data


class EcoRankingSerializer(ModelSerializer):
    image = serializers.SerializerMethodField()
    level = serializers.SerializerMethodField()
    badge = serializers.SerializerMethodField()
    eco_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'image', 'level', 'badge', 'eco_count']

    def get_image(self, data):
        return data.profile.get().image

    def get_level(self, data):
        if data.profile.get().level is None:
            data.profile.update(level=EcoLevel.objects.get(id=1))
        return data.profile.get().level.level

    def get_badge(self, data):
        return EcoLevelSerializer(data.profile.get().level, read_only=True).data['image']

    def get_eco_count(self, data):
        return data.eco.all().count()


class EcoLevelSerializer(ModelSerializer):
    class Meta:
        model = EcoLevel
        fields = ['level', 'image']
