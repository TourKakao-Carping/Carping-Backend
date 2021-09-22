from posts.constants import A_TO_Z_LIST_NUM, POST_INFO_CATEGORY_LIST_NUM
import random

from django.db import models
from django.db.models.expressions import F, Value, Case, Exists, Value, When
from django.db.models.aggregates import Count, Max, Min


class UserPostInfoQuerySet(models.QuerySet):
    """
    인기 TOP 3
    차박에 관한 모든 것
    차에 맞는 차박여행
    """

    # def a_to_z(self):
    # self.all().

    def random_qs(self, count):
        range = self.all().aggregate(max_id=Max("id"), min_id=Min("id"))
        max_id = range["max_id"]
        min_id = range["min_id"]

        pk_arr = []

        i = 0
        while i < A_TO_Z_LIST_NUM:
            pk_arr.append(random.randint(min_id, max_id))
            i += 1

        return self.all().filter(id__in=pk_arr)

    # category function
    # type -> "top3", "carcamp", "campforcar"
    def get_list(self, qs_all, category, count):
        qs = qs_all.filter(category=category)

        if qs.exists():
            qs_count = qs.count()
            if qs_count < POST_INFO_CATEGORY_LIST_NUM:
                return qs[:qs_count]
            else:
                return qs[:count]
        else:
            return qs

    def category_qs(self, count):
        qs_all = self.all().filter(is_approved=True)

        qs_arr = []
        for i in range(1, 4):
            qs_arr.append(self.get_list(qs_all, i, count))

        qs = qs_arr[0] | qs_arr[1] | qs_arr[2]

        return qs

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