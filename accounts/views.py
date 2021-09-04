import datetime
import json
import requests
from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.db.models import Count
from django.http import JsonResponse
from django.shortcuts import redirect
from rest_framework import status

from dj_rest_auth.registration.views import SocialLoginView
from allauth.socialaccount.providers.kakao import views as kakao_view
from allauth.socialaccount.providers.google import views as google_view
from rest_framework.status import HTTP_200_OK
from rest_framework.views import APIView
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken
from rest_framework_simplejwt.tokens import RefreshToken

from accounts.models import Profile, User, EcoLevel
from accounts.serializers import EcoRankingSerializer
from bases.response import APIResponse
from posts.models import EcoCarping

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
    def check_email(self):
        access_token = self.request.data['access_token']
        profile_request = requests.get(
            "https://www.googleapis.com/oauth2/v2/userinfo", headers={"Authorization": f"Bearer {access_token}"})
        profile_json = profile_request.json()
        email = profile_json.get('email')
        user = User.objects.filter(email=email)
        if user.exists():
            return True
        else:
            return False

    def exception(self):
        is_email_user = self.check_email()
        if not is_email_user:
            return JsonResponse({"err_msg": "email already exists."}, status=status.HTTP_400_BAD_REQUEST)
        return super().post

    def get_response(self):
        self.exception()
        user = self.user
        profile_qs = Profile.objects.filter(user=user)
        if profile_qs.exists():
            profile = profile_qs.first()
            profile_image = profile.image
        else:
            profile_image = self.user.socialaccount_set.values(
                "extra_data")[0].get("extra_data")['picture']
            Profile.objects.update_or_create(image=profile_image, user=user)
        profile_data = {
            'image': profile_image,
        }
        response = super().get_response()

        if settings.SIMPLE_JWT['ROTATE_REFRESH_TOKENS']:
            user_refresh = OutstandingToken.objects.filter(user=user)
            if user_refresh.count() > 1:
                last_refresh = user_refresh.order_by(
                    '-created_at')[1].token
                blacklist_refresh = RefreshToken(last_refresh)
                try:
                    blacklist_refresh.blacklist()
                except AttributeError:
                    pass

        del response.data["user"]["first_name"], response.data["user"]["last_name"]
        response.data["user"]["profile"] = profile_data
        return response

    adapter_class = google_view.GoogleOAuth2Adapter


class KakaoLoginView(SocialLoginView):
    def check_email(self):
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
        is_email_user = self.check_email()
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

        if settings.SIMPLE_JWT['ROTATE_REFRESH_TOKENS']:
            user_refresh = OutstandingToken.objects.filter(user=user)
            if user_refresh.count() > 1:
                last_refresh = user_refresh.order_by(
                    '-created_at')[1].token
                blacklist_refresh = RefreshToken(last_refresh)
                try:
                    blacklist_refresh.blacklist()
                except AttributeError:
                    pass

        del response.data["user"]["first_name"], response.data["user"]["last_name"]
        response.data["user"]["profile"] = profile_data

        return response

    adapter_class = kakao_view.KakaoOAuth2Adapter


# 5. 에코랭킹 api - 상위 7개 (프사, 뱃지, 아이디, 순위, 에카포스트 수)
class EcoRankingView(APIView):
    allowed_method = ["GET"]

    def get(self, request):
        response = APIResponse(success=False, code=400)
        eco = User.objects.annotate(
            num_ecos=Count('eco')).order_by('-num_ecos')[:7]
        today = datetime.date.today() + relativedelta(days=1)
        pre_month = today - relativedelta(months=1)
        current_user = request.user

        for i in eco:
            if i.profile.get().level is None or i.eco.count() <= 3:
                i.profile.update(level=EcoLevel.objects.get(id=1))
            elif i.eco.count() <= 8:
                i.profile.update(level=EcoLevel.objects.get(id=2))
            elif i.eco.count() >= 9:
                i.profile.update(level=EcoLevel.objects.get(id=3))

        more_info = {}

        eco_percentage = current_user.eco.count() * 10
        if current_user.eco.count() > 10:
            eco_percentage = 100  # 100% 초과 불가능

        monthly_eco_count = EcoCarping.objects.filter(user_id=current_user.id,
                                                      created_at__range=[pre_month, today]).count()
        more_info['eco_percentage'] = eco_percentage
        more_info['monthly_eco_count'] = monthly_eco_count

        response.success = True
        response.code = 200
        return response.response(data=[EcoRankingSerializer(current_user).data,
                                       more_info,
                                       EcoRankingSerializer(eco, many=True).data])
