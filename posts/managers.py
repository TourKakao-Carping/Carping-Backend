from posts.querysets import UserPostInfoQuerySet
from django.db import models


class UserPostInfoManager(models.Manager):
    def get_queryset(self):
        return UserPostInfoQuerySet(self.model, using=self._db)

    def a_to_z(self):
        return self.get_queryset().a_to_z()

    def like_qs(self, user_pk):
        return self.get_queryset().like_qs(user_pk)

    def random_qs(self, count):
        return self.get_queryset().random_qs(count)

    def category_qs(self, count, user_pk):
        return self.get_queryset().category_qs(count, user_pk)
