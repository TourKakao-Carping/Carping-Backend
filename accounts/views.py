from accounts.adapters import CustomKakaoOAuth2Adapter
from allauth.socialaccount.providers import kakao
from django.shortcuts import render
from django.utils.translation import gettext_lazy as _

from dj_rest_auth.registration.views import SocialLoginView
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from allauth.socialaccount.providers.kakao import views as kakao_view
from allauth.socialaccount.providers.google import views as google_view
from allauth.socialaccount.providers.oauth2.client import OAuth2Client

# Create your views here.


class KakaoLoginView(SocialLoginView):
    adapter_class = CustomKakaoOAuth2Adapter
    # client_class = OAuth2Client
    # callback_url = 'http://localhost:8000/accounts/kakao/login'


class GoogleLoginView(SocialLoginView):
    adapter_class = google_view.GoogleOAuth2Adapter
    # client_class = OAuth2Client
    # callback_url = 'http://localhost:8000/accounts/google/login'
