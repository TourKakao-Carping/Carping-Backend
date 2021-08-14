from camps.querysets import *
from django.db import models


class CampSiteManager(models.Manager):
    def get_queryset(self):
        return CampSiteQuerySet(self.model, using=self._db)

    def autocamp_type(self, count):
        return self.get_queryset().autocamp_type(count)


class AutoCampManager(models.Manager):
    def get_queryset(self):
        return AutoCampQuerySet(self.model, self._db)

    def ordering_views(self, count):
        return self.get_queryset().ordering_views(count)
