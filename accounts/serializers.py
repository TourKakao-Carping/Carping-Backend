from allauth.account.adapter import get_adapter
from dj_rest_auth.registration.serializers import SocialLoginSerializer
from rest_framework import serializers

# class CustomKakaoLoginSerializer(SocialLoginSerializer):
#     serializer_class = SocialLoginSerializer

#     def process_login(self):
#         get_adapter(self.request).login(self.request, self.user)
