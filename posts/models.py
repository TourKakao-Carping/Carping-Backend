from posts.managers import UserPostInfoManager
from django.core.validators import URLValidator
from django.db import models
from django.db.models.deletion import CASCADE
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
    recommend_to = models.CharField(max_length=100, verbose_name=_("추천하는 대상"))
    is_approved = models.BooleanField(default=0, verbose_name=_("관리자 승인여부"))
    like = models.ManyToManyField(
        User, related_name="userpost_like", blank=True)

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


class Store(Base):
    item = models.CharField(max_length=100)
    image = models.ImageField(
        upload_to='img/store/', null=True, blank=True)
    price = models.CharField(max_length=100)
