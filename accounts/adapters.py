
from allauth.socialaccount.providers.kakao.views import KakaoOAuth2Adapter


class CustomKakaoOAuth2Adapter(KakaoOAuth2Adapter):
    def complete_login(self, request, app, token, **kwargs):
        print("!1")
        return super().complete_login(request, app, token, **kwargs)
