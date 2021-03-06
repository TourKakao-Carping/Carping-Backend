from re import I
from posts.constants import CATEGORY_DEACTIVATE
import random

from django.db import models
from django.db.models.expressions import F, Value, Case, Exists, Value, When
from django.db.models.aggregates import Count, Max, Min

import logging

logger = logging.getLogger('random')


class UserPostInfoQuerySet(models.QuerySet):
    """
    인기 TOP 3
    차박에 관한 모든 것
    차에 맞는 차박여행
    """

    def random_qs(self, count, id=False):
        range = self.all().aggregate(max_id=Max("id"), min_id=Min("id"))
        max_id = range["max_id"]
        min_id = range["min_id"]

        pk_arr = []

        i = 0
        while len(pk_arr) < count:
            random_num = random.randint(min_id, max_id)
            if self.all().filter(id=random_num, is_approved=True, author__is_active=True).exists() and not random_num in pk_arr:
                if id and random_num == id:
                    pass
                else:
                    pk_arr.append(random_num)

            i += 1
            if i > max_id - min_id:
                break

        if not len(pk_arr) == count:
            logger.info(pk_arr)

        if len(pk_arr) < 2:
            return self.all().filter(id__gte=min_id, id__lte=max_id, is_approved=True, author__is_active=True)

        return self.all().filter(id__in=pk_arr)

    def like_qs(self, user_pk):
        qs = self.prefetch_related('like')
        is_liked = qs.filter(like=user_pk)

        liked_list = []

        if is_liked.exists():
            liked_list = is_liked.values_list("id", flat=True)

        qs = qs.annotate(like_count=Count("like"),
                         is_liked=Case(
            When(
                id__in=liked_list,
                then=True
            ), default=False
        )
        )

        return qs

    # category function
    # type -> "newbie", "carcamp", "campforcar"
    def get_list(self, qs_all, category, count, user_pk):
        qs = qs_all.filter(category=category)
        qs = qs.like_qs(user_pk)

        if qs.exists():
            qs_count = qs.count()
            if qs_count < count:
                return qs[:qs_count]
            else:
                return qs[:count]
        else:
            return qs

    def category_qs(self, count, user_pk):
        qs_all = self.all().filter(is_approved=True, author__is_active=True).exclude(
            category=CATEGORY_DEACTIVATE).order_by('-created_at')

        qs_arr = []
        for i in range(1, 5):
            qs_arr.append(self.get_list(qs_all, i, count, user_pk))

        qs = qs_arr[0].union(qs_arr[1]).union(qs_arr[2]).union(qs_arr[3])

        return qs

    def user_post_info_detail(self):
        qs_all = self.all().filter(is_approved=True)
        qs_all = qs_all.annotate(thumbnail=F(
            'user_post__thumbnail'), title=F('user_post__title'),
            preview_image1=F('user_post__image1'), preview_image2=F('user_post__image2'),  preview_image3=F('user_post__image3'))

        return qs_all
