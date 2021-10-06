import datetime

from dateutil.relativedelta import relativedelta

from bases.utils import check_str_digit
from posts.models import UserPostPaymentRequest, UserPostInfo


def compute_fee(user, point):
    today = datetime.date.today() + relativedelta(days=1)
    pre_month = today - relativedelta(months=1)
    sale_count = UserPostPaymentRequest.objects.filter(userpost__userpostinfo__author=user).count()
    monthly_post_count = UserPostInfo.objects.filter(author=user,
                                                     created_at__range=[pre_month, today]).count()
    eco_level = user.profile.get().level.level

    if check_str_digit(point):
        point = float(point)

    # 케이스 1 - 첫 포스트 작성 시
    if user.user_post.count() == 0:
        platform_fee = int(float(point) * 0.5)

    # 케이스 2 - 자료판매 0건 이상 / 월 신규 자료등록수 1건 이상 / 에코카핑 지수 1
    elif sale_count >= 0 and monthly_post_count >= 1 and eco_level >= 1:
        platform_fee = int(float(point) * 0.2)

    # 케이스 3 - 자료판매 10건 이상 / 월 신규 자료등록수 3건 이상 / 에코카핑 지수 2
    elif sale_count >= 10 and monthly_post_count >= 3 and eco_level >= 2:
        platform_fee = int(float(point) * 0.15)

    # 케이스 4 - 자료판매 20건 이상 / 월 신규 자료등록수 4건 이상 / 에코카핑 지수 3
    elif sale_count >= 20 and monthly_post_count >= 4 and eco_level >= 3:
        platform_fee = int(float(point) * 0.1)

    else:
        platform_fee = 0

    return platform_fee


def compute_final(user, point):
    if check_str_digit(point):
        point = float(point)

    trade_fee = 500

    # compute_fee 함수 호출 -> 플랫폼 제공 수수료 계산
    platform_fee = compute_fee(user, point)

    withholding_tax = int(float(point) * 0.033)
    vat = int(float(point) * 0.1)

    final_point = int(point) - trade_fee - platform_fee - withholding_tax - vat

    # final_point 최소는 0
    if final_point < 0:
        final_point = 0

    return trade_fee, platform_fee, withholding_tax, vat, final_point
