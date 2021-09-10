from django.core.validators import URLValidator
from django.db import models
from django.db.models.deletion import CASCADE
from taggit.managers import TaggableManager

from accounts.models import User
from bases.models import Base
from bases.functions import upload_user_directory
from camps.models import CampSite


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
    TRASH_CHOICES = (
        ('20L', '20L'),
        ('10L', '10L'),
        ('5L', '5L'),
        ('3L', '3L'),
        ('3L 이하', '3L 이하'),
    )
    trash = models.CharField(max_length=10, choices=TRASH_CHOICES, null=True, blank=True)

    def like_count(self):
        return self.like.values().count()


class Share(Base):
    user = models.ForeignKey(User, on_delete=CASCADE,
                             related_name="share")
    region = models.ForeignKey('Region', on_delete=CASCADE, related_name="share")
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
