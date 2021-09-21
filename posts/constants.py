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
    (1, _("인기 TOP 3")),
    (2, _("차박에 관한 모든 것")),
    (3, _("차에 맞는 차박여행")),
)


A_TO_Z_LIST_NUM = 10

POST_INFO_CATEGORY_LIST_NUM = 3
