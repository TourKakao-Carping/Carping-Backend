import datetime
import json
import random
import re
import time
import requests
import logging

from allauth.socialaccount.models import SocialAccount
from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.db import transaction, DatabaseError
from django.db.models import Count, Prefetch, Q
from django.http import JsonResponse, response
from django.shortcuts import redirect
from rest_framework import status

from dj_rest_auth.registration.views import SocialLoginView
from allauth.socialaccount.providers.kakao import views as kakao_view
from allauth.socialaccount.providers.google import views as google_view
from rest_framework.permissions import AllowAny
from rest_framework.status import HTTP_200_OK
from rest_framework.views import APIView
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken
from rest_framework_simplejwt.tokens import RefreshToken

from accounts.models import Profile, User, EcoLevel, SmsHistory, Certification
from accounts.serializers import EcoRankingSerializer
from bases.response import APIResponse
from bases.utils import make_signature
from posts.models import EcoCarping

BASE_URL = "http://localhost:8000"

KAKAO_CALLBACK_URI = BASE_URL + "/accounts/kakao/callback"
GOOGLE_CALLBACK_URI = BASE_URL + '/accounts/google/callback'

state = getattr(settings, 'STATE')

logger = logging.getLogger('login')


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

        user = User.objects.filter(
            ~Q(socialaccount__provider="google"), email=email)

        if user.exists():
            return True
        else:
            return False

    def exception(self, resposne):
        is_email_user = self.check_email()
        if is_email_user:
            return response.response(error_message="Email Already Exists with Other Provider.")

    def get_response(self):
        user = self.user
        extra_data = self.user.socialaccount_set.get().extra_data
        profile_qs = Profile.objects.filter(user=user)

        if profile_qs.exists():
            profile = profile_qs
        else:
            profile = Profile.objects.update_or_create(
                user=user, image='img/default/default_img.jpg')
        profile_data = {
            'image': profile[0].image.url,
        }

        response = super().get_response()

        if user.username == "" or user.username is None:
            username = extra_data.get('email').split('@')[0]
            User.objects.filter(id=user.id).update(username=username)
            response.data["user"]["username"] = username

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

    def post(self, request):
        response = APIResponse(success=False, code=400)

        data = request.data
        logger.info("Google Login Data Below")
        logger.info(data)

        try:
            self.exception(response)

            req = super().post(request)

            # return req
            response.success = True
            response.code = 200
            return JsonResponse(req.data)
        except BaseException as e:
            # logger.info("Account Error :" + str(e))
            return response.response(error_message=str(e))

    adapter_class = google_view.GoogleOAuth2Adapter


class KakaoLoginView(SocialLoginView):
    def check_email(self):
        access_token = self.request.data['access_token']
        profile_request = requests.get(
            "https://kapi.kakao.com/v2/user/me", headers={"Authorization": f"Bearer {access_token}"})
        profile_json = profile_request.json()

        kakao_account = profile_json.get('kakao_account')
        email = kakao_account.get('email')

        user = User.objects.filter(
            ~Q(socialaccount__provider="kakao"), email=email)

        if user.exists():
            return True
        else:
            return False

    def exception(self, response):
        is_email_user = self.check_email()
        if is_email_user:
            return response.response(error_message="Email Already Exists with Other Provider.")

    def get_response(self):
        user = self.user
        profile_qs = Profile.objects.filter(user=user)
        extra_data = self.user.socialaccount_set.get().extra_data

        kakao_account = extra_data.get("kakao_account")

        if profile_qs.exists():
            profile = profile_qs.first()
        else:
            profile = kakao_account.get('profile')
            gender = profile.get('gender')
            profile = Profile.objects.create(
                gender=gender, user=user, image='img/default/default_img.jpg')

        profile_data = {
            "image": profile.image.url
        }

        response = super().get_response()

        if user.username == "" or user.username is None:
            username = kakao_account.get('profile').get('nickname')
            User.objects.filter(id=user.id).update(username=username)
            response.data["user"]["username"] = username

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

    def post(self, request):
        response = APIResponse(success=False, code=400)
        data = request.data

        logger.info("Kakao Login Data Below")
        logger.info(data)

        try:
            self.exception(response)

            req = super().post(request)
            # return req
            response.success = True
            response.code = 200
            return JsonResponse(req.data)
        except BaseException as e:
            logger.info("Kakao Account Error :" + str(e))
            return response.response(error_message=str(e))

    adapter_class = kakao_view.KakaoOAuth2Adapter


# 5. 에코랭킹 api - 상위 7개 (프사, 뱃지, 아이디, 순위, 에코포스트 수)
class EcoRankingView(APIView):
    allowed_method = ["GET"]

    def get(self, request):
        response = APIResponse(success=False, code=400)
        eco = User.objects.exclude(is_active=False).annotate(
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


# 인증 문자 전송
class SmsSendView(APIView):
    def send_sms(self, phone_num, auth_num):
        timestamp = str(int(time.time() * 1000))
        headers = {
            'Content-Type': "application/json; charset=UTF-8",
            'x-ncp-apigw-timestamp': timestamp,  # 네이버 API 서버와 5분이상 시간차이 발생 시 오류
            'x-ncp-iam-access-key': str(getattr(settings, 'NAVER_ACCESS_KEY')),
            'x-ncp-apigw-signature-v2': make_signature(timestamp)
        }
        body = {
            "type": "SMS",
            "contentType": "COMM",
            "from": "01072376542",
            "content": f"[Carping(카핑)] 인증번호 [{auth_num}]를 입력해주세요.",
            "messages": [{"to": f"{phone_num}"}]
        }
        body = json.dumps(body)
        uri = f"https://sens.apigw.ntruss.com/sms/v2/services/{getattr(settings, 'NAVER_PROJECT_ID')}/messages"
        response = requests.post(uri, headers=headers, data=body)
        return response.text

    def post(self, request):
        response = APIResponse(success=False, code=400)
        user = request.user
        phone_num = request.data.get('phone')

        regex = re.compile('\d{11}')

        if not regex.match(phone_num):
            return response.response(error_message="휴대폰 번호는 '-' 없이 입력해주세요.")

        auth_num = random.randint(10000, 100000)  # 랜덤숫자 생성, 5자리

        send = self.send_sms(phone_num=phone_num, auth_num=auth_num)

        if "success" in send:
            Profile.objects.filter(user=user).update(phone=phone_num)
            SmsHistory.objects.create(user_id=user.pk, auth_num=auth_num)

            response.success = True
            response.code = 200
            return response.response(data=[{"message": "인증번호 발송"}])

        else:
            return response.response(error_message=f"{send}")


# 문자 인증번호와 사용자가 입력한 인증번호 비교
class SMSVerificationView(APIView):
    def post(self, request):
        response = APIResponse(success=False, code=400)
        user = request.user
        try:
            auth_num = SmsHistory.objects.filter(
                user_id=user.pk).order_by('-id')[0].auth_num
            fail_count = SmsHistory.objects.get(
                user_id=user.pk, auth_num=auth_num).fail_count

            if fail_count >= 3:
                response.success = True
                response.code = 200
                return response.response(data=[{"message": "인증 문자 발송을 다시 요청해주세요."}])

            if str(auth_num) == str(request.data.get('auth_num')):
                SmsHistory.objects.filter(user_id=user.pk, auth_num=auth_num).update(
                    auth_num_check=auth_num)
                Certification.objects.update_or_create(
                    user=user, authorized=True)
                response.success = True
                response.code = 200
                return response.response(data=[{"message": "인증 완료"}])

            else:
                fail_count += 1
                SmsHistory.objects.filter(user_id=user.pk, auth_num=auth_num).update(
                    auth_num_check=request.data.get('auth_num'), fail_count=fail_count)
                response.success = True
                response.code = 200
                return response.response(data=[{"message": "인증 실패"}])

        except Exception as e:
            response.code = status.HTTP_404_NOT_FOUND
            return response.response(error_message=str(e))


# 회원탈퇴 - 유저 포스트는 삭제하면 안됨(결제내역과 묶여있음)
class UserWithdrawView(APIView):
    def post(self, request):
        response = APIResponse(success=False, code=400)
        user = request.user
        try:
            with transaction.atomic():
                # 초기화 - 프로필(에코레벨은 1), 유저 정보, 인증 정보
                profile = Profile.objects.filter(user=user)
                user_obj = User.objects.filter(id=user.id)
                if profile is None or user_obj is None:
                    raise Exception('No user instance or profile instance')

                number = User.objects.filter(is_active=False).count()
                number += 1

                profile.update(phone=None, image='img/default/default_img.jpg',
                               level=1, bio=None, interest=None,
                               author_comment="탈퇴한 유저입니다.", account_num=None)
                user_obj.update(
                    is_active=False, email=f"{number}@withdrew.com", username=f"탈퇴유저 {number}")

                # 삭제 - 차박지, 에코카핑, 무료나눔, 무료포스트, 검색기록, 댓글, 리뷰,
                # 스크랩, 좋아요, 휴대폰 인증 내역, 인증 정보
                user.autocamp.all().delete()
                user.eco.all().delete()
                user.share.all().delete()
                user.search.all().delete()
                user.review.all().delete()
                user.comment.all().delete()

                user.userpost_like.through.objects.filter(user=user).delete()
                user.eco_like.through.objects.filter(user=user).delete()
                user.share_like.through.objects.filter(user=user).delete()
                user.review_like.through.objects.filter(user=user).delete()
                user.comment_like.through.objects.filter(user=user).delete()

                user.campsite_bookmark.through.objects.filter(
                    user=user).delete()
                user.autocamp_bookmark.through.objects.filter(
                    user=user).delete()

                SmsHistory.objects.filter(user_id=user.id).delete()
                Certification.objects.filter(user=user).delete()
                SocialAccount.objects.filter(user=user).delete()

                response.success = True
                response.code = 200
                return response.response(data=[{"message": "탈퇴 완료"}])

        except Exception as e:
            return response.response(error_message=str(e))
