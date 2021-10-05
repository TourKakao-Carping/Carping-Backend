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
    (-99, _("비활성화")),
)

CATEGORY_BASE = 0
CATEGORY_NEWBIE = 1
CATEGORY_ALL_FOR_CAR = 2
CATEGORY_FIT_CAR = 3
CATEGORY_DEACTIVATE = -99


BANK_CHOICES = (
    (0, _("카카오뱅크")),
    (1, _("농협")),
    (2, _("신한")),
    (3, _("IBK기업")),
    (4, _("하나")),
    (5, _("우리")),
    (6, _("국민")),
    (7, _("SC제일")),
    (8, _("대구")),
    (9, _("부산")),
    (10, _("광주")),
    (11, _("새마을금고")),
    (12, _("경남")),
    (13, _("전북")),
    (14, _("제주")),
    (15, _("산업")),
    (16, _("우체국")),
    (17, _("신협")),
    (18, _("수협")),
    (19, _("씨티")),
    (20, _("케이뱅크")),
    (21, _("도이치")),
    (22, _("BOA")),
    (23, _("BNP")),
    (24, _("중국공상")),
    (25, _("HSBC")),
    (26, _("JP모간")),
    (27, _("산림조합")),
    (28, _("저축은행")),
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

SEARCH_TYPE_CHOICES = (
    (0, _("메인 차박지")),
    (1, _("포스트")),
)

A_TO_Z_LIST_NUM = 3

POST_INFO_CATEGORY_LIST_NUM = 3
