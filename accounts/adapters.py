
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
        uid = extra_data.get("id")
        if SocialAccount.objects.filter(uid=uid).exists():
            # return JsonResponse({"error_code": "USER_EXISTS", "message": "exists"})
            pass
        else:
            kakao_account = extra_data.get("kakao_account")
            profile = kakao_account.get("profile")
            nickname = profile.get("nickname")
            profile_image = profile.get("profile_image_url")
            Profile.objects.create(nickname=nickname, image=profile_image,)
        return self.get_provider().sociallogin_from_response(request, extra_data)
