from camps.querysets import *
from django.db import models


class CampSiteManager(models.Manager):
    def get_queryset(self):
        return CampSiteQuerySet(self.model, using=self._db)

    def autocamp_type(self, count):
        return self.get_queryset().autocamp_type(count)

    def theme_brazier(self, sort):
        return self.get_queryset().theme_brazier(sort)

    def theme_animal(self, sort):
        return self.get_queryset().theme_animal(sort)

    def theme_season(self, select, sort):
        return self.get_queryset().theme_season(select, sort)

    def theme_program(self, sort):
        return self.get_queryset().theme_program(sort)

    def theme_event(self, sort):
        return self.get_queryset().theme_event(sort)


class AutoCampManager(models.Manager):
    def get_queryset(self):
        return AutoCampQuerySet(self.model, self._db)

    def ordering_views(self, count):
        return self.get_queryset().ordering_views(count)
