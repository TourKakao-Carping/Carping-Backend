from posts.models import UserPostPaymentRequest
import requests
from django.conf import settings
from django.db import transaction, DatabaseError


class KakaoPayClient(object):
    BASE_URL = "http://chanjongp.co.kr"
    ADMIN_KEY = getattr(settings, "KAKAO_APP_ADMIN_KEY")
    READY_URL = 'https://kapi.kakao.com/v1/payment/ready'
    APPROVE_URL = 'https://kapi.kakao.com/v1/payment/approve'

    headers = {
        "Authorization": "KakaoAK " + f"{ADMIN_KEY}",
        "Content-type": "application/x-www-form-urlencoded;charset=utf-8",
    }

    def ready(self, user, userpost):
        try:
            with transaction.atomic():
                success = True

                userpost_info = userpost.userpostinfo_set.get()
                point = userpost_info.point

                payment_req = UserPostPaymentRequest.objects.create(
                    user=user, userpost=userpost, total_amount=point, tax_free_amount=100)

                params = {
                    "cid": "TC0ONETIME",    # 테스트용 코드
                    "partner_order_id": f"{payment_req.pk}",     # 주문번호
                    "partner_user_id": f"{user.pk}",    # 유저 아이디
                    "item_name": f"{userpost.title}",        # 구매 물품 이름
                    "quantity": "1",                # 구매 물품 수량
                    # 구매 물품 가격
                    "total_amount": f"{payment_req.total_amount}",
                    "tax_free_amount": "100",         # 구매 물품 비과세
                    "approval_url": self.BASE_URL + "/success",
                    "cancel_url": self.BASE_URL + "/cancel",
                    "fail_url": self.BASE_URL + "/fail",
                }

                res = requests.post(
                    self.READY_URL, headers=self.headers, params=params)

                res_json = res.json()

                tid = res_json.pop('tid')
                created_at = res_json.pop('created_at')

                payment_req.tid = tid
                payment_req.ready_requested_at = created_at

                payment_req.save()

                return success, res_json
        except DatabaseError as e:
            success = False
            return success, str(e)
