import re
from allauth.socialaccount.models import SocialAccount
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.deletion import CASCADE
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import BaseUserManager, AbstractUser
from django.utils import timezone

from bases.functions import upload_user_directory
from bases.models import Base


def validate_phone(value):
    regex = re.compile('\d{2,3}-\d{3,4}-\d{4}')
    if not regex.match(value):
        raise ValidationError("O-O-O 형식의 번호를 입력해주세요.")


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
    badge = models.ForeignKey('Badge', null=True, on_delete=CASCADE, related_name="user", )
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

    phone = models.CharField(max_length=50, null=True,
                             blank=True, validators=[validate_phone])
    image = models.URLField(null=True)
    gender = models.IntegerField(default=0, null=True)
    level = models.ForeignKey('EcoLevel', on_delete=CASCADE, related_name="user", default=1)
    bio = models.TextField(null=True, blank=True)
    INTEREST_CHOICES = (
        ('차크닉', '차크닉'),
        ('혼차박', '혼차박'),
        ('퇴근박', '퇴근박'),
        ('불멍', '불멍'),
        ('바베큐', '바베큐'),
        ('오지캠핑', '오지캠핑'),
        ('레저', '레저'),
        ('낚시', '낚시'),
        ('클린 차박', '클린 차박'),
    )
    interest = models.CharField(max_length=10, choices=INTEREST_CHOICES, null=True, blank=True)
    user = models.ForeignKey(User, on_delete=CASCADE,
                             related_name="profile", null=True)
    # socialaccount = models.ForeignKey(
    #     SocialAccount, on_delete=CASCADE, null=True, related_name="socialaccount_fk")

    objects = ProfileManager()


class Certification(Base):
    user = models.ForeignKey(User, on_delete=CASCADE, related_name="certification")
    marketing = models.BooleanField(default=1)
    authorized = models.BooleanField(default=0)


class Badge(Base):
    name = models.CharField(max_length=50)
    image = models.ImageField(
        upload_to='img/badge/', null=True, blank=True)
