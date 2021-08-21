from django.db import models


class CampSiteQuerySet(models.QuerySet):

    def autocamp_type(self, count):
        return self.all().order_by('-views')[:count]

    def theme_brazier(self, sort):
        qs = self.all().filter(brazier="가능")
        if sort == "recent":
            return qs.order_by('-created_at')
        elif sort == "popular":
            return qs.order_by('views')

    def theme_animal(self, sort):
        qs = self.all().filter(animal__contains="가능")
        if sort == "recent":
            return qs.order_by('-created_at')
        if sort == "popular":
            return qs.order_by('views')

    def theme_season(self, select, sort):
        # select : 봄, 여름 , 가을, 겨울
        qs = self.all().filter(season__contains=f"{select}")
        if sort == "recent":
            return qs.order_by('-created_at')
        if sort == "popular":
            return qs.order_by('views')


class AutoCampQuerySet(models.QuerySet):

    def ordering_views(self, count):
        return self.all().order_by('-views')[:count]
