from django.db import models
from django.db.models.deletion import CASCADE
from taggit.managers import TaggableManager

from accounts.models import User
from bases.models import Base
from camps.models import CampSite


class Post(Base):
    user = models.ForeignKey(User, on_delete=CASCADE, related_name="post", null=True)
    campsite = models.ForeignKey(CampSite, on_delete=CASCADE, related_name="post", null=True)
    title = models.CharField(max_length=100, null=False)
    text = models.TextField()
    views = models.IntegerField(default=0)
    tags = TaggableManager(blank=True)


class EcoCarping(Base):
    user = models.ForeignKey(User, on_delete=CASCADE, related_name="eco", null=True)
    latitude = models.FloatField(null=False)
    longitude = models.FloatField(null=False)
    image = models.CharField(max_length=100, null=True)
    title = models.CharField(max_length=100, null=False)
    text = models.TextField()
    tags = TaggableManager(blank=True)


class Share(Base):
    user = models.ForeignKey(User, on_delete=CASCADE, related_name="share", null=True)
    latitude = models.FloatField(null=False)
    longitude = models.FloatField(null=False)
    image = models.CharField(max_length=100, null=True)
    title = models.CharField(max_length=100, null=False)
    text = models.TextField()
    tags = TaggableManager(blank=True)
