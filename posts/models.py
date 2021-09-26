from posts.managers import UserPostInfoManager
from django.core.validators import URLValidator
from django.db import models
from django.db.models.deletion import CASCADE, PROTECT
from django.db.models.fields.related import ForeignKey
from taggit.managers import TaggableManager

from accounts.models import User
from bases.models import Base
from bases.functions import upload_user_directory, upload_user_directory_userpost
from camps.models import CampSite
from posts.constants import *


from django.utils.translation import ugettext_lazy as _


class Post(Base):
    user = models.ForeignKey(User, on_delete=CASCADE,
                             related_name="post")
    title = models.CharField(max_length=100, null=False)
    thumbnail = models.ImageField(
        upload_to=upload_user_directory, null=True, blank=True)
    views = models.IntegerField(default=0)
    tags = TaggableManager(blank=True)
    campsite1 = models.ForeignKey(
        CampSite, on_delete=CASCADE, related_name="post1", null=True)
    sub_title1 = models.CharField(max_length=100, null=True)
    text1 = models.TextField()
    image1 = models.ImageField(upload_to=upload_user_directory, null=True)
    source1 = models.CharField(max_length=255, null=True)
    campsite2 = models.ForeignKey(
        CampSite, on_delete=CASCADE, related_name="post2", null=True, blank=True)
    sub_title2 = models.CharField(max_length=100, null=True)
    text2 = models.TextField(null=True, blank=True)
    image2 = models.ImageField(
        upload_to=upload_user_directory, null=True, blank=True)
    source2 = models.CharField(max_length=255, null=True, blank=True)
    campsite3 = models.ForeignKey(
        CampSite, on_delete=CASCADE, related_name="post3", null=True, blank=True)
    sub_title3 = models.CharField(max_length=100, null=True, blank=True)
    text3 = models.TextField(null=True, blank=True)
    image3 = models.ImageField(
        upload_to=upload_user_directory, null=True, blank=True)
    source3 = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.title


class EcoCarping(Base):
    user = models.ForeignKey(User, on_delete=CASCADE,
                             related_name="eco")
    latitude = models.FloatField(null=False)
    longitude = models.FloatField(null=False)
    place = models.CharField(max_length=100, default="장소")
    image1 = models.ImageField(
        upload_to=upload_user_directory, null=True, blank=True)
    image2 = models.ImageField(
        upload_to=upload_user_directory, null=True, blank=True)
    image3 = models.ImageField(
        upload_to=upload_user_directory, null=True, blank=True)
    image4 = models.ImageField(
        upload_to=upload_user_directory, null=True, blank=True)
    title = models.CharField(max_length=100, null=False)
    text = models.CharField(max_length=500)
    tags = TaggableManager(blank=True)
    like = models.ManyToManyField(
        User, related_name="eco_like", blank=True)
    trash = models.CharField(
        max_length=10, choices=TRASH_CHOICES, null=True, blank=True)

    def like_count(self):
        return self.like.values().count()


class Share(Base):
    user = models.ForeignKey(User, on_delete=CASCADE,
                             related_name="share")
    region = models.ForeignKey(
        'Region', on_delete=CASCADE, related_name="share")
    image1 = models.ImageField(
        upload_to=upload_user_directory, null=True, blank=True)
    image2 = models.ImageField(
        upload_to=upload_user_directory, null=True, blank=True)
    image3 = models.ImageField(
        upload_to=upload_user_directory, null=True, blank=True)
    image4 = models.ImageField(
        upload_to=upload_user_directory, null=True, blank=True)
    title = models.CharField(max_length=100, null=False)
    text = models.CharField(max_length=500)
    chat_addr = models.TextField(validators=[URLValidator()])
    tags = TaggableManager(blank=True)
    is_shared = models.BooleanField(default=False)
    like = models.ManyToManyField(
        User, related_name="share_like", blank=True)


class Region(Base):
    sido = models.CharField(max_length=50)
    sigungu = models.CharField(max_length=50, null=True)
    dong = models.CharField(max_length=50)


class UserPost(Base):
    title = models.CharField(max_length=100)
    thumbnail = models.ImageField(
        upload_to=upload_user_directory_userpost)

    sub_title1 = models.CharField(max_length=100)
    text1 = models.TextField()
    image1 = models.ImageField(
        upload_to=upload_user_directory_userpost, null=True, blank=True)

    sub_title2 = models.CharField(max_length=100, null=True, blank=True)
    text2 = models.TextField(null=True, blank=True)
    image2 = models.ImageField(
        upload_to=upload_user_directory_userpost, null=True, blank=True)

    sub_title3 = models.CharField(max_length=100, null=True, blank=True)
    text3 = models.TextField(null=True, blank=True)
    image3 = models.ImageField(
        upload_to=upload_user_directory_userpost, null=True, blank=True)

    sub_title4 = models.CharField(max_length=100, null=True, blank=True)
    text4 = models.TextField(null=True, blank=True)
    image4 = models.ImageField(
        upload_to=upload_user_directory_userpost, null=True, blank=True)

    sub_title5 = models.CharField(max_length=100, null=True, blank=True)
    text5 = models.TextField(null=True, blank=True)
    image5 = models.ImageField(
        upload_to=upload_user_directory_userpost, null=True, blank=True)

    def __str__(self):
        return self.title


class UserPostInfo(Base):
    author = models.ForeignKey(
        User, on_delete=CASCADE, related_name="post_author")
    user_post = models.ForeignKey(UserPost, on_delete=CASCADE)
    category = models.IntegerField(
        default=0, choices=CATEGORY_CHOICES, verbose_name=_("카테고리")
    )
    pay_type = models.IntegerField(
        default=0, choices=PAY_CHOICES, verbose_name=_("유/무료 여부"))
    point = models.IntegerField(default=0, verbose_name=_("가격"))
    info = models.CharField(max_length=100, verbose_name=_("포스트 소개"))
    kakao_openchat_url = models.URLField(null=True, blank=True)
    author_comment = models.CharField(
        max_length=100, verbose_name=_("작가의 한마디"))
    recommend_to = models.CharField(max_length=100, verbose_name=_("추천하는 대상"))
    is_approved = models.BooleanField(default=0, verbose_name=_("관리자 승인여부"))
    like = models.ManyToManyField(
        User, related_name="userpost_like", blank=True)
    views = models.IntegerField(default=0)

    objects = UserPostInfoManager()

    def review_count(self):
        return self.review.values().count()

    def star1_avg(self):
        if self.review_count() == 0:
            return 0
        return round(self.review.aggregate(models.Avg('star1'))['star1__avg'], 1)

    def star2_avg(self):
        if self.review_count() == 0:
            return 0
        return round(self.review.aggregate(models.Avg('star2'))['star2__avg'], 1)

    def star3_avg(self):
        if self.review_count() == 0:
            return 0
        return round(self.review.aggregate(models.Avg('star3'))['star3__avg'], 1)

    def star4_avg(self):
        if self.review_count() == 0:
            return 0
        return round(self.review.aggregate(models.Avg('star4'))['star4__avg'], 1)

    def total_star_avg(self):
        if self.review_count() == 0:
            return 0
        return round(self.review.aggregate(models.Avg('total_star'))['total_star__avg'], 1)

    def __str__(self):
        return self.user_post.title

# 이 테이블의 pk가 카카오페이 API 요청 시의 partner_order_id와 일치


class UserPostPaymentRequest(Base):
    user = models.ForeignKey(User, on_delete=PROTECT, verbose_name=_("구매자"))
    userpost = models.ForeignKey(
        UserPost, on_delete=PROTECT, verbose_name=_("유저 포스트"))
    total_amount = models.IntegerField(verbose_name=_("결제총액"))
    tax_free_amount = models.IntegerField(verbose_name=_("상품 비과세 금액"))
    vat_amount = models.IntegerField(default=0, verbose_name=_("상품 부가세 금액"))
    tid = models.CharField(max_length=50, verbose_name=_(
        "결제 고유번호"), null=True, blank=True)
    pg_token = models.CharField(max_length=100, verbose_name=_(
        "결제 승인 요청 토큰"), null=True, blank=True)
    status = models.IntegerField(
        default=0,  choices=PAY_STATUS_CHOICES, verbose_name=_("결제요청 상태"))
    ready_requested_at = models.DateTimeField(null=True, blank=True)


class UserPostPaymentApprovalResult(Base):
    payment_request = models.ForeignKey(
        UserPostPaymentRequest, on_delete=PROTECT, verbose_name=_("주문번호"))
    aid = models.CharField(max_length=50, verbose_name=_("요청 고유 번호"))
    payment_type = models.IntegerField(
        choices=PAY_TYPE_CHOICES, verbose_name=_("결제 수단"))
    # amount
    total_amount = models.IntegerField(verbose_name=_("결제총액"))
    tax_free_amount = models.IntegerField(verbose_name=_("상품 비과세 금액"))
    vat_amount = models.IntegerField(default=0, verbose_name=_("상품 부가세 금액"))
    # card_info
    card_info = models.TextField(null=True, blank=True)
    item_name = models.CharField(max_length=100)

    ready_requested_at = models.DateTimeField()
    approved_at = models.DateTimeField()


class Store(Base):
    item = models.CharField(max_length=100)
    image = models.ImageField(
        upload_to='img/store/', null=True, blank=True)
    price = models.CharField(max_length=100)
