from bases.utils import check_distantce
from django.db import models
from django.db.models.expressions import F, Value

from django.utils.translation import ugettext as _


class CampSiteQuerySet(models.QuerySet):

    def autocamp_type(self, count):
        return self.all().order_by('-views')[:count]

    # 불멍
    def theme_brazier(self, sort):
        qs = self.all().exclude(brazier=None).exclude(
            brazier=_('불가')).filter(type__contains=_("자동차야영장"))
        if sort == "recent":
            return qs.order_by('-created_at')
        elif sort == "popular":
            return qs.order_by('views')
        else:
            return qs

    # 반려
    def theme_animal(self, sort):
        qs = self.all().filter(animal=_("가능"), type__contains=_("자동차야영장"))
        if sort == "recent":
            return qs.order_by('-created_at')
        if sort == "popular":
            return qs.order_by('views')
        else:
            return qs

    # 여행시기
    def theme_season(self, select, sort):
        # select : 봄, 여름 , 가을,
        if select == None:
            qs = self.all()
        else:
            qs = self.all().filter(
                season__contains=f"{select}", type=_("일반야영장"))

        if sort == "recent":
            return qs.order_by('-created_at')
        if sort == "popular":
            return qs.order_by('views')
        else:
            return qs

    # 체험
    def theme_program(self, sort):
        qs = self.all().filter(prgram__isnull=False, type__contains=_("자동차야영장"))
        if sort == "recent":
            return qs.order_by('-created_at')
        if sort == "popular":
            return qs.order_by('views')

    # 문화행사
    def theme_event(self, sort):
        qs = self.all().filter(event__isnull=False, type__contains=_("자동차야영장"))
        if sort == "recent":
            return qs.order_by('-created_at')
        if sort == "popular":
            return qs.order_by('views')
        else:
            return qs

    # 레포츠
    def theme_leports(self, select, sort):
        """
        '수상레저', '액티비티', '스키', '항공레저', '낚시'
        """
        leports = [_("수상레저"), _("액티비티"), _("스키"), _("항공레저"), _("낚시")]

        if select in leports:
            qs = self.all().filter(
                themenv__contains=f"{select}", type__contains=_("자동차야영장"))
        else:
            qs = self.all().filter(themenv__in=leports, type__contains=_("자동차야영장"))

        if sort == "recent":
            return qs.order_by('-created_at')
        if sort == "popular":
            return qs.order_by('views')
        else:
            return qs

    # 레포츠
    def theme_nature(self, select, sort):
        """
        '가을단풍명소', '걷기길', '여름물놀이', '봄꽃여행', '일몰명소', '일출명소', '겨울눈꽃명소'
        """
        nature = [_("가을단풍명소"), _("걷기길"), _("봄꽃여행"),
                  _("일몰명소"), _("일출명소"), _("겨울눈꽃명소")]

        if select in nature:
            qs = self.all().filter(
                themenv__contains=f"{select}", type__contains=_("자동차야영장"))
        else:
            qs = self.all().filter(themenv__in=nature, type__contains=_("자동차야영장"))

        if sort == "recent":
            return qs.order_by('-created_at')
        if sort == "popular":
            return qs.order_by('views')
        else:
            return qs

    # 기타야영장
    def theme_other_type(self, select, sort):
        """
        '일반야영장', '글램핑', '카라반'
        """
        other_type = [_("일반야영장"), _("글램핑"), _("카라반")]
        if select == None:
            qs = self.all().filter(type__in=other_type)
        else:
            qs = self.all().filter(type__contains=f"{select}")

        if sort == "recent":
            return qs.order_by('-created_at')
        if sort == "popular":
            return qs.order_by('views')
        else:
            return qs


class AutoCampQuerySet(models.QuerySet):

    def ordering_views(self, count):
        return self.all().order_by('-views')[:count]
