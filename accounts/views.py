import json
import requests
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import redirect
from django.utils.translation import gettext_lazy as _
from rest_framework import status


from dj_rest_auth.registration.views import SocialLoginView
from allauth.socialaccount.providers.kakao import views as kakao_view
from allauth.socialaccount.providers.google import views as google_view
from allauth.socialaccount.models import SocialAccount

from accounts.models import Profile, User

BASE_URL = "http://localhost:8000"

KAKAO_CALLBACK_URI = BASE_URL + "/accounts/kakao/callback"
GOOGLE_CALLBACK_URI = BASE_URL + '/accounts/google/callback'

state = getattr(settings, 'STATE')


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
        raise json.encoder.JSONDecodeError(error)
    access_token = token_req_json.get("access_token")
    """
    Email Request
    """
    profile_request = requests.get(
        "https://kapi.kakao.com/v2/user/me", headers={"Authorization": f"Bearer {access_token}"})
    profile_json = profile_request.json()
    kakao_account = profile_json.get('kakao_account')
    return JsonResponse({"access_token": access_token, "kakao_account": kakao_account},
                        json_dumps_params={'ensure_ascii': False})


def google_login(request):
    scope = "https://www.googleapis.com/auth/userinfo.email"
    client_id = getattr(settings, 'GOOGLE_OAUTH2_CLIENT_ID')
    return redirect(f"https://accounts.google.com/o/oauth2/v2/auth?client_id="
                    f"{client_id}&response_type=code&redirect_uri={GOOGLE_CALLBACK_URI}&scope={scope}")


def google_callback(request):
    client_id = getattr(settings, 'GOOGLE_OAUTH2_CLIENT_ID')
    client_secret = getattr(settings, 'GOOGLE_OAUTH2_CLIENT_SECRET')
    code = request.GET.get('code')
    """
    Access Token Request
    """
    token_req = requests.post(
        f"https://oauth2.googleapis.com/token?client_id={client_id}&client_secret="
        f"{client_secret}&code={code}&grant_type=authorization_code&redirect_uri={GOOGLE_CALLBACK_URI}&state={state}")
    token_req_json = token_req.json()
    error = token_req_json.get("error")
    if error is not None:
        raise json.encoder.JSONDecodeError(error)
    access_token = token_req_json.get('access_token')
    return JsonResponse({"access_token": access_token}, json_dumps_params={'ensure_ascii': False})


class GoogleLoginView(SocialLoginView):
    def exception(self):
        user = self.user
        social_user = SocialAccount.objects.get(user=user)
        if social_user is None:
            return JsonResponse({'err_msg': 'email exists but not social user'}, status=status.HTTP_400_BAD_REQUEST)
        if social_user.provider != 'google':
            return JsonResponse({'err_msg': 'no matching social type'}, status=status.HTTP_400_BAD_REQUEST)
        return super().post

    def get_response(self):
        self.exception()
        user = self.user
        access_token = self.request.data['access_token']
        response = super().get_response()

        profile_request = requests.get(
            "https://www.googleapis.com/oauth2/v2/userinfo", headers={"Authorization": f"Bearer {access_token}"})
        profile_json = profile_request.json()
        profile_image_url = profile_json.get('picture')
        profile = Profile.objects.update_or_create(
            image=profile_image_url, user=user)
        profile_data = {
            'image': profile[0].image,
        }
        del response.data["user"]["first_name"], response.data["user"]["last_name"]
        response.data["user"]["profile"] = profile_data
        return response

    adapter_class = google_view.GoogleOAuth2Adapter


class KakaoLoginView(SocialLoginView):
    def get_email(self):
        access_token = self.request.data['access_token']
        profile_request = requests.get(
            "https://kapi.kakao.com/v2/user/me", headers={"Authorization": f"Bearer {access_token}"})
        profile_json = profile_request.json()
        kakao_account = profile_json.get('kakao_account')
        email = kakao_account.get('email')
        user = User.objects.filter(email=email)
        if user.exists():
            return True
        else:
            return False

    def exception(self):
        is_email_user = self.get_email()
        if not is_email_user:
            return JsonResponse({"err_msg": "email already exists."}, status=status.HTTP_400_BAD_REQUEST)
        return super().post

    def get_response(self):
        self.exception()
        user = self.user
        profile_qs = Profile.objects.filter(user=user)
        if profile_qs.exists():
            profile = profile_qs.first()
        else:
            extra_data = self.user.socialaccount_set.values("extra_data")[
                0].get("extra_data")
            kakao_account = extra_data.get("kakao_account")
            profile = kakao_account.get('profile')
            profile_image = profile.get('profile_image_url')
            gender = profile.get('gender')
            profile = Profile.objects.create(
                image=profile_image, gender=gender, user=user)

        profile_data = {
            "image": profile.image
        }

        response = super().get_response()
        del response.data["user"]["first_name"], response.data["user"]["last_name"]
        response.data["user"]["profile"] = profile_data

        return response

    adapter_class = kakao_view.KakaoOAuth2Adapter
