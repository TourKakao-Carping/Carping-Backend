from django.db import models

from camps.querysets import *


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

    def theme_leports(self, select, sort):
        return self.get_queryset().theme_leports(select, sort)

    def theme_nature(self, select, sort):
        return self.get_queryset().theme_nature(select, sort)

    def theme_other_type(self, select, sort):
        return self.get_queryset().theme_other_type(select, sort)

    def bookmark_qs(self, user_pk):
        return self.get_queryset().bookmark_qs(user_pk)


class AutoCampManager(models.Manager):
    def get_queryset(self):
        return AutoCampQuerySet(self.model, self._db)

    def ordering_views(self, count):
        return self.get_queryset().ordering_views(count)
