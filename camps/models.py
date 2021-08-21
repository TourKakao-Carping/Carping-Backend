from django.db import models
from django.db.models.deletion import CASCADE
from taggit.managers import TaggableManager

from bases.functions import upload_user_directory
from camps.managers import AutoCampManager, CampSiteManager

from accounts.models import User
from bases.models import Base


class CampSite(models.Model):
    user = models.ForeignKey(User, on_delete=CASCADE,
                             related_name="campsite", null=True)
    name = models.CharField(max_length=50, null=True)
    lat = models.FloatField(null=True)
    lon = models.FloatField(null=True)
    animal = models.CharField(max_length=50, null=True)
    event = models.CharField(max_length=255, null=True)
    program = models.CharField(max_length=255, null=True)
    brazier = models.CharField(max_length=10, null=True)
    website = models.CharField(max_length=255, null=True)
    phone = models.CharField(max_length=50, null=True)
    address = models.CharField(max_length=100, null=True)
    oper_day = models.CharField(max_length=50, null=True)
    off_start = models.CharField(max_length=50, null=True)
    off_end = models.CharField(max_length=50, null=True)
    faculty = models.CharField(max_length=10, null=True)
    permission_date = models.CharField(max_length=50, null=True)
    reservation = models.CharField(max_length=50, null=True)
    toilet = models.IntegerField(default=0, null=True)
    shower = models.IntegerField(default=0, null=True)
    type = models.CharField(max_length=50, null=True)
    sub_facility = models.CharField(max_length=255, null=True)
    season = models.CharField(max_length=50, null=True)
    image = models.URLField(null=True, blank=True)
    views = models.IntegerField(default=0)
    area = models.CharField(max_length=50, null=False)
    bookmark = models.ManyToManyField(
        User, related_name="campsite_bookmark", blank=True)
    themenv = models.CharField(max_length=255, null=True)
    created_at = models.DateTimeField(null=True)
    updated_at = models.DateTimeField(null=True)

    objects = CampSiteManager()

    def __str__(self):
        return self.name


class AutoCamp(Base):
    user = models.ForeignKey(User, on_delete=CASCADE,
                             related_name="autocamp", null=True)
    latitude = models.FloatField(null=False)
    longitude = models.FloatField(null=False)
    image = models.ImageField(
        upload_to=upload_user_directory, null=True, blank=True)
    title = models.CharField(max_length=100, null=False)
    text = models.TextField()
    views = models.IntegerField(default=0)
    tags = TaggableManager(blank=True)
    bookmark = models.ManyToManyField(
        User, related_name="autocamp_bookmark", blank=True)

    objects = AutoCampManager()
