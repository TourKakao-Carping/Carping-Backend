from allauth.socialaccount.models import SocialAccount
from django.db import models
from django.db.models.deletion import CASCADE
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import BaseUserManager, AbstractUser
from django.utils import timezone


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


class User(AbstractUser):
    # username = None
    email = models.EmailField(unique=True, max_length=255)
    first_name = None
    last_name = None
    # USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return self.email


class ProfileManager(models.Manager):
    # @classmethod
    # def normalize_email(cls, email):
    #     """
    #     Normalize the email address by lowercasing the domain part of it.
    #     """
    #     email = email or ""
    #     try:
    #         email_name, domain_part = email.strip().rsplit("@", 1)
    #     except ValueError:
    #         pass
    #     else:
    #         email = email_name + "@" + domain_part.lower()
    #     return email

    def create(self, **extra_fields):
        # officer_email = self.normalize_email(officer_email)
        profile = self.model(**extra_fields)
        profile.save()
        return profile


class Profile(models.Model):
    """
    nickname                닉네임
    birthdate               생년월일
    image                   프로필 사진
    gender                  성별

    """

    nickname = models.CharField(max_length=50)
    birthdate = models.CharField(max_length=20, null=True)
    image = models.URLField(null=True)
    gender = models.IntegerField(default=0)
    user = models.ForeignKey(User, on_delete=CASCADE,
                             related_name="user_fk", null=True)
    # socialaccount = models.ForeignKey(
    #     SocialAccount, on_delete=CASCADE, null=True, related_name="socialaccount_fk")

    objects = ProfileManager()
