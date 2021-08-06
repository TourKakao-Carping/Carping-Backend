from django.db import models
from django.db.models.deletion import CASCADE

from accounts.models import User
from bases.models import Base


class CampSite(Base):
    user = models.ForeignKey(User, on_delete=CASCADE, related_name="campsite", null=True)
    name = models.CharField(max_length=50, null=False)
    latitude = models.FloatField(null=False)
    longitude = models.FloatField(null=False)
    animal = models.CharField(max_length=50, null=True)
    brazier = models.CharField(max_length=10, null=True)
    website = models.CharField(max_length=255, null=True)
    phone = models.CharField(max_length=50, null=True)
    address = models.CharField(max_length=100, null=False)
    oper_day = models.CharField(max_length=50, null=True)
    off_day_start = models.CharField(max_length=50, null=True)
    off_day_end = models.CharField(max_length=50, null=True)
    faculty = models.CharField(max_length=10, null=True)
    permission_date = models.CharField(max_length=50, null=True)
    reservation = models.CharField(max_length=50, null=True)
    toilet = models.IntegerField(default=0, null=False)
    shower = models.IntegerField(default=0, null=False)
    type = models.CharField(max_length=50, null=False)
    sub_facility = models.CharField(max_length=255, null=True)
    season = models.CharField(max_length=50, null=True)
    image = models.URLField(null=True, blank=True)
    views = models.IntegerField(default=0)
    area = models.CharField(max_length=50, null=False)


class AutoCamp(Base):
    user = models.ForeignKey(User, on_delete=CASCADE, related_name="autocamp", null=True)
    latitude = models.FloatField(null=False)
    longitude = models.FloatField(null=False)
    image = models.CharField(max_length=100, null=True)
    title = models.CharField(max_length=100, null=False)
    text = models.TextField()
    views = models.IntegerField(default=0)
