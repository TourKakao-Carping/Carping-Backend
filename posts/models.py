from django.db import models
from django.db.models.deletion import CASCADE
from taggit.managers import TaggableManager

from accounts.models import User
from bases.models import Base
from camps.models import CampSite


class Post(Base):
    user = models.ForeignKey(User, on_delete=CASCADE,
                             related_name="post", null=True)
    title = models.CharField(max_length=100, null=False)
    thumbnail = models.CharField(max_length=100, null=True)
    views = models.IntegerField(default=0)
    tags = TaggableManager(blank=True)
    campsite1 = models.ForeignKey(
        CampSite, on_delete=CASCADE, related_name="post1", null=True)
    sub_title1 = models.CharField(max_length=100, null=True)
    text1 = models.TextField()
    image1 = models.CharField(max_length=255, null=True)
    source1 = models.CharField(max_length=255, null=True)
    campsite2 = models.ForeignKey(
        CampSite, on_delete=CASCADE, related_name="post2", null=True, blank=True)
    sub_title2 = models.CharField(max_length=100, null=True)
    text2 = models.TextField(null=True, blank=True)
    image2 = models.CharField(max_length=255, null=True, blank=True)
    source2 = models.CharField(max_length=255, null=True, blank=True)
    campsite3 = models.ForeignKey(
        CampSite, on_delete=CASCADE, related_name="post3", null=True, blank=True)
    sub_title3 = models.CharField(max_length=100, null=True, blank=True)
    text3 = models.TextField(null=True, blank=True)
    image3 = models.CharField(max_length=255, null=True, blank=True)
    source3 = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.title


class EcoCarping(Base):
    user = models.ForeignKey(User, on_delete=CASCADE,
                             related_name="eco", null=True)
    latitude = models.FloatField(null=False)
    longitude = models.FloatField(null=False)
    image = models.CharField(max_length=100, null=True)
    title = models.CharField(max_length=100, null=False)
    text = models.TextField()
    tags = TaggableManager(blank=True)


class Share(Base):
    user = models.ForeignKey(User, on_delete=CASCADE,
                             related_name="share", null=True)
    latitude = models.FloatField(null=False)
    longitude = models.FloatField(null=False)
    image = models.CharField(max_length=100, null=True)
    title = models.CharField(max_length=100, null=False)
    text = models.TextField()
    tags = TaggableManager(blank=True)
