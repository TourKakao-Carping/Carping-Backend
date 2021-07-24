import jwt
import requests
from json import JSONDecodeError
from django.http import JsonResponse
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from dj_rest_auth.registration.views import SocialLoginView

from accounts.adapters import CustomKakaoOAuth2Adapter

from accounts.models import User
from accounts.serializers import GoogleLoginSerializer
from carping.settings import JWT_SECRET


# 닉네임 휴대폰 등 추가 정보 받아와서 프로필 모델에 업데이트해야 함
@api_view(("POST",))
def google_login_view(request):
    serializer = GoogleLoginSerializer(data=request.data)
    if serializer.is_valid(raise_exception=True):
        access_token = serializer.validated_data["access_token"]
        email_req = requests.get(
            f"https://www.googleapis.com/oauth2/v1/tokeninfo?access_token={access_token}")
        email_req_status = email_req.status_code

        if email_req_status != 200:
            return Response({'err_msg': 'failed to get email'}, status=status.HTTP_400_BAD_REQUEST)
        email_req_json = email_req.json()
        email = email_req_json.get('email')

        # profile_request = requests.get(
        #     "https://www.googleapis.com/oauth2/v2/userinfo", headers={"Authorization": f"Bearer {access_token}"})
        # profile_json = profile_request.json()
        # error = profile_json.get("error")
        # if error is not None:
        #     raise JSONDecodeError(error)
        # print("구글 계정", profile_json)

        user, created = User.objects.update_or_create(email=email)

        token = jwt.encode({'id': user.id},
                           JWT_SECRET, algorithm='HS256')

        return JsonResponse({
            'token': token,
            'email': email,
            'username': user.username,
        }, json_dumps_params={'ensure_ascii': False}, status=200)


class KakaoLoginView(SocialLoginView):
    adapter_class = CustomKakaoOAuth2Adapter
    # client_class = OAuth2Client
    # callback_url = 'http://localhost:8000/accounts/kakao/login'
