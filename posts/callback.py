from urllib.parse import parse_qs

from posts.constants import PAY_STATUS_FAIL
from bases.payment import KakaoPayClient
from rest_framework.views import APIView
from bases.response import APIResponse
from posts.models import UserPostPaymentRequest, UserPostPaymentApprovalResult

from django.utils.translation import ugettext_lazy as _


class UserPostFailCallbackAPIView(APIView):

    def get(self, request, pk):
        response = APIResponse(success=False, code=400)

        try:
            payment_req = UserPostPaymentRequest.objects.get(id=pk)
            payment_req.status = PAY_STATUS_FAIL

            payment_req.save()

            response.success = True
            response.code = 200

            return response.response(data=_("결제가 실패하였습니다. 다시 시도해 주세요."))

        except UserPostPaymentRequest.DoesNotExist:
            response.response(error_message=_("Not Found"))


class UserPostCancelCallbackAPIView(APIView):

    def get(self, request, pk):
        kakao_pay = KakaoPayClient()
        response = APIResponse(success=False, code=400)

        try:
            payment_req = UserPostPaymentRequest.objects.get(id=pk)

            success, status = kakao_pay.cancel(payment_req)

            if success:
                response.success = True
                response.code = 200

                return response.response(data=status)
            else:

                return response.response(data=status)
        except UserPostPaymentRequest.DoesNotExist:
            response.response(error_message=_("Not Found"))


class UserPostSuccessCallbackAPIView(APIView):

    def get(self, request, pk):
        kakao_pay = KakaoPayClient()
        user = request.user
        query_params = request.META['QUERY_STRING']
        params = parse_qs(query_params)
        pg_token = params["pg_token"][0]
        response = APIResponse(success=False, code=400)

        try:
            payment_req = UserPostPaymentRequest.objects.get(id=pk)

            success, status = kakao_pay.approve(user, pg_token, payment_req)

            if success:
                response.success = True
                response.code = 200
                return response.response(data=status)
            else:
                return response.response(error_message=status)

        except UserPostPaymentRequest.DoesNotExist:
            response.response(error_message=_("Not Found"))
        return response.response()
