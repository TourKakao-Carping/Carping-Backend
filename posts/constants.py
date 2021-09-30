from django.utils.translation import ugettext_lazy as _


TRASH_CHOICES = (
    ('20L', '20L'),
    ('10L', '10L'),
    ('5L', '5L'),
    ('3L', '3L'),
    ('3L 이하', '3L 이하'),
)

PAY_CHOICES = (
    (0, _("무료")),
    (1, _("유료")),
)

CATEGORY_CHOICES = (
    (0, _("기본")),
    (1, _("초보 차박러를 위한 포스트")),
    (2, _("차박에 관한 모든 것")),
    (3, _("차에 맞는 차박여행")),
)

PAY_STATUS_CHOICES = (
    (0, _("대기중")),
    (1, _("성공")),
    (2, _("실패")),
    (3, _("취소")),
    (4, _("에러케이스"))
)


PAY_STATUS_SUCCESS = 1
PAY_STATUS_FAIL = 2
PAY_STATUS_CANCEL = 3
PAY_STATUS_ERROR = 4


PAY_TYPE_CHOICES = (
    (0, _("CARD")),
    (1, _("MONEY")),
)

PAY_TYPE = {
    "CARD": 0,
    "MONEY": 1
}

A_TO_Z_LIST_NUM = 3

POST_INFO_CATEGORY_LIST_NUM = 3
