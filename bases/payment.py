from posts.models import UserPostPaymentApprovalResult, UserPostPaymentRequest
import requests
from django.conf import settings
from django.db import transaction, DatabaseError

from posts.constants import PAY_STATUS_CANCEL, PAY_STATUS_ERROR, PAY_TYPE


class KakaoPayClient(object):
    BASE_URL = "http://localhost:8000/posts/"
    ADMIN_KEY = getattr(settings, "KAKAO_APP_ADMIN_KEY")
    READY_URL = 'https://kapi.kakao.com/v1/payment/ready'
    APPROVE_URL = 'https://kapi.kakao.com/v1/payment/approve'
    STATUS_URL = 'https://kapi.kakao.com//v1/payment/order'
    cid = getattr(settings, "CID")

    headers = {
        "Authorization": "KakaoAK " + f"{ADMIN_KEY}",
        "Content-type": "application/x-www-form-urlencoded;charset=utf-8",
    }

    def ready(self, user, userpost):
        try:
            with transaction.atomic():

                userpost_info = userpost.userpostinfo_set.get()
                point = userpost_info.point

                payment_req = UserPostPaymentRequest.objects.create(
                    user=user, userpost=userpost, total_amount=point, tax_free_amount=100)

                req_obj_id = payment_req.id

                params = {
                    "cid": f"{self.cid}",    # 테스트용 코드
                    "partner_order_id": f"{payment_req.pk}",     # 주문번호
                    "partner_user_id": f"{user.pk}",    # 유저 아이디
                    "item_name": f"{userpost.title}",        # 구매 물품 이름
                    "quantity": "1",                # 구매 물품 수량
                    "total_amount": f"{payment_req.total_amount}",  # 구매 물품 가격
                    "tax_free_amount": "100",         # 구매 물품 비과세
                    "approval_url": self.BASE_URL + f"user-post/callback/{req_obj_id}/success",
                    "cancel_url": self.BASE_URL + f"user-post/callback/{req_obj_id}/cancel",
                    "fail_url": self.BASE_URL + f"user-post/callback/{req_obj_id}/fail",
                }

                res = requests.post(
                    self.READY_URL, headers=self.headers, params=params)
                if res.status_code == 200:
                    res_json = res.json()
                    tid = res_json.pop('tid')
                    created_at = res_json.pop('created_at')

                    payment_req.tid = tid
                    payment_req.ready_requested_at = created_at

                    payment_req.save()

                    return True, res_json
                else:
                    return False, "fail"

        except DatabaseError as e:
            success = False
            return success, str(e)

    def cancel(self, payment_req):
        params = {
            "cid": f"{self.cid}",
            "tid": f"{payment_req.tid}"
        }

        res = requests.post(
            self.STATUS_URL, headers=self.headers, params=params)

        if res.status_code == 200:
            res_json = res.json()

            status = res_json.get('status')
            if status == "QUIT_PAYMENT":
                payment_req.status = PAY_STATUS_CANCEL
                payment_req.save()

                return True, "cancel"
            else:
                payment_req.status = PAY_STATUS_ERROR
                payment_req.save()

                return False, status

    def approve(self, user, pg_token, payment_req):
        params = {
            "cid": f"{self.cid}",
            "tid": f"{payment_req.tid}",
            "partner_order_id": f"{payment_req.pk}",     # 주문번호
            "partner_user_id": f"{payment_req.user.pk}",    # 유저 아이디
            "pg_token": f"{pg_token}"
        }

        res = requests.post(
            self.APPROVE_URL, headers=self.headers, params=params)

        res_json = res.json()
        print(res_json)
        if res.status_code == 200:

            aid = res_json.get('aid')
            payment_type = res_json.get('payment_method_type')
            item_name = res_json.get('item_name')

            amount = res_json.get('amount')
            total_amount = amount.get('total')
            tax_free_amount = amount.get('tax_free')
            vat_amount = amount.get('vat')

            card_info = amount.get('card_info')
            ready_requested_at = amount.get('created_at')
            approved_at = amount.get('approved_at')

            with transaction.atomic():
                UserPostPaymentApprovalResult.objects.create(aid=aid, payment_type=PAY_TYPE[payment_type], total_amount=total_amount, tax_free_amount=tax_free_amount, vat_amount=vat_amount, card_info=str(
                    card_info), item_name=item_name, ready_requested_at=ready_requested_at, approved_at=approved_at, payment_request=payment_req)

                return True, "결제가 완료되었습니다."

        else:
            extras = res_json.get('extras')
            message = extras.get('method_result_message')

            return False, message
