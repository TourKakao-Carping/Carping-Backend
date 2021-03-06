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
    thumbnail_with_text = models.ImageField(
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
    place = models.CharField(max_length=100, default="??????")
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

    def like_count(self):
        return self.like.values().count()


class Region(Base):
    sido = models.CharField(max_length=50)
    sigungu = models.CharField(max_length=50, null=True)
    dong = models.CharField(max_length=50)


class UserPost(Base):
    title = models.CharField(max_length=100, verbose_name=_("??????"))
    thumbnail = models.ImageField(
        upload_to=upload_user_directory_userpost, verbose_name=_("?????????"))

    sub_title1 = models.CharField(max_length=100, verbose_name=_("1 - ?????????"))
    text1 = models.TextField(verbose_name=_("1 - ??????"))
    image1 = models.ImageField(
        upload_to=upload_user_directory_userpost, null=True, blank=True, verbose_name=_("1 - ?????????"))

    sub_title2 = models.CharField(
        max_length=100, null=True, blank=True, verbose_name=_("2 - ?????????"))
    text2 = models.TextField(null=True, blank=True, verbose_name=_("2 - ??????"))
    image2 = models.ImageField(
        upload_to=upload_user_directory_userpost, null=True, blank=True, verbose_name=_("2 - ?????????"))

    sub_title3 = models.CharField(
        max_length=100, null=True, blank=True, verbose_name=_("3 - ?????????"))
    text3 = models.TextField(null=True, blank=True, verbose_name=_("3 - ??????"))
    image3 = models.ImageField(
        upload_to=upload_user_directory_userpost, null=True, blank=True, verbose_name=_("3 - ?????????"))

    sub_title4 = models.CharField(
        max_length=100, null=True, blank=True, verbose_name=_("4 - ?????????"))
    text4 = models.TextField(null=True, blank=True, verbose_name=_("4 - ??????"))
    image4 = models.ImageField(
        upload_to=upload_user_directory_userpost, null=True, blank=True, verbose_name=_("4 - ?????????"))

    sub_title5 = models.CharField(
        max_length=100, null=True, blank=True, verbose_name=_("5 - ?????????"))
    text5 = models.TextField(null=True, blank=True, verbose_name=_("5 - ??????"))
    image5 = models.ImageField(
        upload_to=upload_user_directory_userpost, null=True, blank=True, verbose_name=_("5 - ?????????"))

    approved_user = models.ManyToManyField(
        User, blank=True, related_name='approved_user', verbose_name=_("????????????"))

    def __str__(self):
        return self.title


class UserPostInfo(Base):
    author = models.ForeignKey(
        User, on_delete=CASCADE, related_name="user_post", verbose_name=_("?????????"))
    user_post = models.ForeignKey(UserPost, on_delete=CASCADE)
    category = models.IntegerField(
        default=0, choices=CATEGORY_CHOICES, verbose_name=_("????????????")
    )
    pay_type = models.IntegerField(
        default=0, choices=PAY_CHOICES, verbose_name=_("???/?????? ??????"))
    point = models.IntegerField(default=0, verbose_name=_("?????? ??????"))
    trade_fee = models.IntegerField(default=0, verbose_name=_("?????? ?????????"))
    platform_fee = models.IntegerField(default=0, verbose_name=_("????????? ?????? ?????????"))
    withholding_tax = models.IntegerField(
        default=0, verbose_name=_("????????? ???????????? 3.3%"))
    vat = models.IntegerField(default=0, verbose_name=_("VAT 10%"))
    final_point = models.IntegerField(default=0, verbose_name=_("?????? ?????????"))
    bank = models.IntegerField(
        default=0, choices=BANK_CHOICES, null=True, blank=True, verbose_name=_("??????"))
    info = models.CharField(max_length=100, verbose_name=_("????????? ??????"))
    kakao_openchat_url = models.URLField(
        null=True, blank=True, verbose_name=_("????????? ????????? URL"))
    recommend_to = models.CharField(max_length=100, verbose_name=_("???????????? ??????"))
    is_approved = models.BooleanField(
        default=0, choices=IS_APPROVED_CHOICES, verbose_name=_("????????? ????????????"))
    like = models.ManyToManyField(
        User, related_name="userpost_like", blank=True)
    views = models.IntegerField(default=0, verbose_name=_("?????????"))
    rejected_reason = models.IntegerField(
        default=0, choices=REJECTED_CHOICES, verbose_name=_("????????????"))

    objects = UserPostInfoManager()

    def review_count(self):
        return self.review.values().count()

    def like_count(self):
        return self.like.values().count()

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

# ??? ???????????? pk??? ??????????????? API ?????? ?????? partner_order_id??? ??????


class UserPostPaymentRequest(Base):
    user = models.ForeignKey(User, on_delete=PROTECT, verbose_name=_("?????????"))
    userpost = models.ForeignKey(
        UserPost, on_delete=PROTECT, verbose_name=_("?????? ?????????"))
    total_amount = models.IntegerField(verbose_name=_("????????????"))
    tax_free_amount = models.IntegerField(verbose_name=_("?????? ????????? ??????"))
    vat_amount = models.IntegerField(default=0, verbose_name=_("?????? ????????? ??????"))
    tid = models.CharField(max_length=50, verbose_name=_(
        "?????? ????????????"), null=True, blank=True)
    status = models.IntegerField(
        default=0,  choices=PAY_STATUS_CHOICES, verbose_name=_("???????????? ??????"))
    ready_requested_at = models.DateTimeField(null=True, blank=True)


class UserPostPaymentApprovalResult(Base):
    payment_request = models.ForeignKey(
        UserPostPaymentRequest, on_delete=PROTECT, verbose_name=_("????????????"))
    aid = models.CharField(max_length=50, verbose_name=_("?????? ?????? ??????"))
    payment_type = models.IntegerField(
        choices=PAY_TYPE_CHOICES, verbose_name=_("?????? ??????"))
    # amount
    total_amount = models.IntegerField(verbose_name=_("????????????"))
    tax_free_amount = models.IntegerField(verbose_name=_("?????? ????????? ??????"))
    vat_amount = models.IntegerField(default=0, verbose_name=_("?????? ????????? ??????"))
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
