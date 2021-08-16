from django.db import models
from django.db.models.deletion import CASCADE

from accounts.models import User
from bases.models import Base
from camps.models import CampSite, AutoCamp
from posts.models import Post, EcoCarping, Share


class Review(Base):
    user = models.ForeignKey(User, on_delete=CASCADE, related_name="review", null=False)
    autocamp = models.ForeignKey(AutoCamp, on_delete=CASCADE, related_name="review", null=True, blank=True)
    post = models.ForeignKey(Post, on_delete=CASCADE, related_name="review", null=True, blank=True)
    text = models.TextField()
    image = models.CharField(max_length=100)
    star1 = models.IntegerField()
    star2 = models.IntegerField()
    star3 = models.IntegerField()
    star4 = models.IntegerField()
    total_star = models.IntegerField()


class Comment(Base):
    user = models.ForeignKey(User, on_delete=CASCADE, related_name="comment", null=False)
    ecocarping = models.ForeignKey(EcoCarping, on_delete=CASCADE, related_name="comment", null=True, blank=True)
    share = models.ForeignKey(Share, on_delete=CASCADE, related_name="comment", null=True, blank=True)
    text = models.CharField(max_length=50)
    root = models.ForeignKey('self', related_name='root_comment', on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return '{} : {}'.format(self.user, self.text)


class Like(Base):
    user = models.ForeignKey(User, on_delete=CASCADE, related_name="like", null=False)
    post = models.ForeignKey(Post, on_delete=CASCADE, related_name="like", null=True, blank=True)
    ecocarping = models.ForeignKey(EcoCarping, on_delete=CASCADE, related_name="like", null=True, blank=True)
    review = models.ForeignKey(Review, on_delete=CASCADE, related_name="like", null=True, blank=True)
    comment = models.ForeignKey(Comment, on_delete=CASCADE, related_name="like", null=True, blank=True)
    count = models.IntegerField(default=0)


class BookMark(Base):
    user = models.ForeignKey(User, on_delete=CASCADE, related_name="bookmark", null=False)
    post = models.ForeignKey(Post, on_delete=CASCADE, related_name="bookmark", null=True, blank=True)
    autocamp = models.ForeignKey(AutoCamp, on_delete=CASCADE, related_name="bookmark", null=True, blank=True)
    campsite = models.ForeignKey(CampSite, on_delete=CASCADE, related_name="bookmark", null=True, blank=True)
