import re
from random import randint

from allauth.socialaccount.models import SocialAccount
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.deletion import CASCADE
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import BaseUserManager, AbstractUser

from multiselectfield import MultiSelectField

from bases.functions import upload_user_directory
from bases.models import Base
from posts.constants import SEARCH_TYPE_CHOICES


class UserManager(BaseUserManager):
    """
    Custom user model manager where email is the unique identifiers
    for authentication instead of usernames.
    """

    def create_user(self, username, password, **extra_fields):
        """
        Create and save a User with the given username and password.
        """
        if not username:
            raise ValueError(_("The username must be set"))
        # username = self.normalize_username(username)
        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, username, password, **extra_fields):
        """
        Create and save a SuperUser with the given email and password.
        """
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError(_("Superuser must have is_staff=True."))
        if extra_fields.get("is_superuser") is not True:
            raise ValueError(_("Superuser must have is_superuser=True."))
        return self.create_user(username, password, **extra_fields)


class User(AbstractUser, Base):
    # username = None
    email = models.EmailField(unique=True, max_length=255)
    first_name = None
    last_name = None
    date_joined = None
    # USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        if self.username == "":
            return self.email
        else:
            return self.username


class EcoLevel(Base):
    level = models.IntegerField(default=1, null=True)
    image = models.ImageField(
        upload_to='img/badge/', null=True, blank=True)


class ProfileManager(models.Manager):
    def create(self, **extra_fields):
        profile = self.model(**extra_fields)
        profile.save()
        return profile


class Profile(Base):
    """
    phone                   휴대폰 번호
    image                   프로필 사진
    gender                  성별
    """
    phone = models.CharField(max_length=50, null=True, blank=True)
    image = models.ImageField(
        upload_to=upload_user_directory, default='img/default/default_img.jpg')
    gender = models.IntegerField(default=0, null=True)
    level = models.ForeignKey(
        'EcoLevel', on_delete=CASCADE, related_name="user", default=1)
    bio = models.TextField(null=True, blank=True)
    INTEREST_CHOICES = (
        (0, '🚗차크닉'),
        (1, '⛺혼차박'),
        (2, '🌆퇴근박'),
        (3, '🔥불멍'),
        (4, '🍖바베큐'),
        (5, '🏕오지캠핑'),
        (6, '🏄레저'),
        (7, '🎣낚시'),
        (8, '🌱클린 차박'),
    )
    interest = MultiSelectField(
        choices=INTEREST_CHOICES, null=True, blank=True)
    user = models.ForeignKey(User, on_delete=CASCADE,
                             related_name="profile", null=True)
    # socialaccount = models.ForeignKey(
    #     SocialAccount, on_delete=CASCADE, null=True, related_name="socialaccount_fk")
    author_comment = models.CharField(
        max_length=100, verbose_name=_("작가의 한마디"), null=True, blank=True)
    account_num = models.CharField(
        max_length=255, null=True, blank=True, verbose_name=_("계좌번호"))

    objects = ProfileManager()


class Certification(Base):
    user = models.ForeignKey(User, on_delete=CASCADE,
                             related_name="certification")
    marketing = models.BooleanField(default=1)
    authorized = models.BooleanField(default=0)


class SmsHistory(Base):
    user_id = models.IntegerField(verbose_name='유저 pk')
    auth_num = models.IntegerField(verbose_name='인증 번호')
    auth_num_check = models.IntegerField(verbose_name='인증 번호 확인', null=True)
    fail_count = models.IntegerField(default=0, verbose_name='실패 횟수')


class Search(Base):
    user = models.ForeignKey(User, on_delete=CASCADE, related_name="search")
    keyword = models.CharField(max_length=255)
    name = models.CharField(max_length=500)
    type = models.IntegerField(
        default=0, choices=SEARCH_TYPE_CHOICES, verbose_name='메인/포스트')

    def same_keyword_count(self, obj):
        return self.objects.filter(keyword=obj.name).count()

    def same_camp_search_count(self, obj):
        return self.objects.filter(name=obj.name).count()
