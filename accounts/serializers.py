from allauth.account.adapter import get_adapter
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework_simplejwt.tokens import RefreshToken


class CustomTokenRefreshSerializer(serializers.Serializer):
    refresh_token = serializers.CharField()
    access_token = serializers.ReadOnlyField()

    def validate(self, attrs):
        refresh = RefreshToken(attrs['refresh_token'])

        data = {'access_token': str(refresh.access_token)}
        return data
