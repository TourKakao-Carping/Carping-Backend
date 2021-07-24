import json
from django.http.response import JsonResponse
import requests
from accounts.adapters import CustomKakaoOAuth2Adapter
from allauth.socialaccount.providers import kakao
from django.shortcuts import redirect, render
from django.utils.translation import gettext_lazy as _
from dj_rest_auth.registration.views import SocialLoginView
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from allauth.socialaccount.providers.kakao import views as kakao_view
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from django.core import serializers
# Create your views here.
from django.conf import settings
from accounts.models import Profile, User
from allauth.socialaccount.models import SocialAccount

from rest_framework import status
from json.decoder import JSONDecodeError


BASE_URL = "http://chanjongp.co.kr"
KAKAO_CALLBACK_URI = BASE_URL + "/accounts/kakao/callback"


def kakao_login(request):
    rest_api_key = getattr(settings, 'KAKAO_REST_API_KEY')
    return redirect(
        f"https://kauth.kakao.com/oauth/authorize?client_id={rest_api_key}&redirect_uri={KAKAO_CALLBACK_URI}&response_type=code"
    )


def kakao_callback(request):
    rest_api_key = getattr(settings, 'KAKAO_REST_API_KEY')
    code = request.GET.get("code")
    redirect_uri = KAKAO_CALLBACK_URI
    """
    Access Token Request
    """
    token_req = requests.get(
        f"https://kauth.kakao.com/oauth/token?grant_type=authorization_code&client_id={rest_api_key}&redirect_uri={redirect_uri}&code={code}")
    token_req_json = token_req.json()
    error = token_req_json.get("error")
    if error is not None:
        raise JSONDecodeError(error)
    access_token = token_req_json.get("access_token")
    """
    Email Request
    """
    profile_request = requests.get(
        "https://kapi.kakao.com/v2/user/me", headers={"Authorization": f"Bearer {access_token}"})
    profile_json = profile_request.json()
    # print(profile_json)
    kakao_account = profile_json.get('kakao_account')
    print(kakao_account)
    """
    nickname
    profile_image_url
    email
    birthday
    gender

    kakao_account에서 이메일 외에
    카카오톡 프로필 이미지, 배경 이미지 url 가져올 수 있음
    print(kakao_account) 참고
    """
    # print(kakao_account)
    email = kakao_account.get('email')
    return JsonResponse({"access_token": access_token, "kakao_account": kakao_account}, json_dumps_params={'ensure_ascii': False})


class KakaoLoginView(APIView):
    permission_classes = [AllowAny, ]

    def post(self, request):
        data = json.loads(request.body)
        access_token = data.get("access_token")
        """
        Email Request
        """

        profile_request = requests.get(
            "https://kapi.kakao.com/v2/user/me", headers={"Authorization": f"Bearer {access_token}"})
        profile_request.raise_for_status()
        profile_json = profile_request.json()
        kakao_account = profile_json.get('kakao_account')
        profile = kakao_account.get('profile')
        birthday = kakao_account.get('birthday')
        email = kakao_account.get('email')
        nickname = profile.get('nickname')
        profile_image_url = profile.get('profile_image_url')
        gender = profile.get('gender')
        if gender == "male":
            gender = 0
        else:
            gender = 1

        """
        nickname
        profile_image_url
        email
        birthday
        gender
        """
        try:
            user = User.objects.get(email=email)
            # 기존에 가입된 유저의 Provider가 kakao가 아니면 에러 발생, 맞으면 로그인
            # 다른 SNS로 가입된 유저
            social_user = SocialAccount.objects.get(user=user)
            # if social_user is None:
            #     return JsonResponse({'err_msg': 'email exists but not social user'}, status=status.HTTP_400_BAD_REQUEST)
            if social_user.provider != 'kakao':
                return JsonResponse({'err_msg': 'no matching social type'}, status=status.HTTP_400_BAD_REQUEST)
            # 기존에 Google로 가입된 유저
            data = {'access_token': access_token}
            accept = requests.post(
                f"{BASE_URL}/accounts/login/kakao/finish", data=data)
            accept_status = accept.status_code
            if accept_status != 200:
                return JsonResponse({'err_msg': 'failed to signin'}, status=accept_status)
            accept_json = accept.json()

            profile = Profile.objects.filter(user=user)
            if profile.exists():
                profile = profile[0]
            profile_data = {"email": user.email, "nickname": profile.nickname,
                            "profile_image": profile.image}
            accept_json['user'] = profile_data
            # accept_json.pop('user', None)
            # accept_json['user'] = profile
            return JsonResponse(accept_json, json_dumps_params={'ensure_ascii': False})
        except User.DoesNotExist:
            # 기존에 가입된 유저가 없으면 새로 가입
            data = {'access_token': access_token}
            accept = requests.post(
                f"{BASE_URL}/accounts/login/kakao/finish", data=data)
            accept_status = accept.status_code
            if accept_status != 200:
                return JsonResponse({'err_msg': 'failed to signup'}, status=accept_status)
            # user의 pk, email, first name, last name과 Access Token, Refresh token 가져옴
            accept_json = accept.json()
            user_id = accept_json['user'].get('pk')
            user = User.objects.filter(id=user_id)
            if user.exists():
                user = user[0]
            # Profile 생성
            profile = Profile.objects.create(
                nickname=nickname, birthdate=birthday, image=profile_image_url, gender=gender, user=user)
            profile_data = {
                "email": user.email, "nickname": profile.nickname, "profile_image": profile.image}
            accept_json['user'] = profile_data
            return JsonResponse(accept_json, json_dumps_params={'ensure_ascii': False})


class KakaoLoginViewFinish(SocialLoginView):
    adapter_class = CustomKakaoOAuth2Adapter
    # adapter_class = kakao_view.KakaoOAuth2Adapter
    # client_class = OAuth2Client
    # callback_url = 'http://localhost:8000/accounts/kakao/login'
