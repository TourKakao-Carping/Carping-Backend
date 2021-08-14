from django.db import models


class CampSiteQuerySet(models.QuerySet):

    def autocamp_type(self, count):
        return self.all().order_by('-views')[:count]


class AutoCampQuerySet(models.QuerySet):

    def ordering_views(self, count):
        return self.all().order_by('-views')[:count]
