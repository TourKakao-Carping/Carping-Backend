
from django.http.response import JsonResponse
import requests
from accounts.models import Profile
from allauth.socialaccount.models import SocialAccount
from allauth.socialaccount.providers.kakao.views import KakaoOAuth2Adapter


class CustomKakaoOAuth2Adapter(KakaoOAuth2Adapter):
    def complete_login(self, request, app, token, **kwargs):
        headers = {"Authorization": "Bearer {0}".format(token.token)}
        resp = requests.get(self.profile_url, headers=headers)
        resp.raise_for_status()
        extra_data = resp.json()

        make_account = self.get_provider().sociallogin_from_response(request, extra_data)
        # uid = extra_data.get("id")
        # social_account = SocialAccount.objects.filter(uid=uid)
        # if not social_account.exists():
        #     user = social_account[0].user
        #     kakao_account = extra_data.get("kakao_account")
        #     profile = kakao_account.get("profile")
        #     nickname = profile.get("nickname")
        #     profile_image = profile.get("profile_image_url")
        #     Profile.objects.create(
        #         nickname=nickname, image=profile_image, user=user)
        return make_account
        # return self.get_provider().sociallogin_from_response(request, extra_data)
