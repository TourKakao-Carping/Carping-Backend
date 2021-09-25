from django.db import models
from django.db.models.deletion import CASCADE

from accounts.models import User
from bases.functions import upload_user_directory
from bases.models import Base
from camps.models import CampSite, AutoCamp
from posts.models import Post, EcoCarping, Share, UserPost, UserPostInfo


class Review(Base):
    user = models.ForeignKey(User, on_delete=CASCADE,
                             related_name="review", null=False)
    autocamp = models.ForeignKey(
        AutoCamp, on_delete=CASCADE, related_name="review", null=True, blank=True)
    post = models.ForeignKey(Post, on_delete=CASCADE,
                             related_name="review", null=True, blank=True)
    userpostinfo = models.ForeignKey(
        UserPostInfo, on_delete=CASCADE, related_name="review", null=True, blank=True)
    text = models.TextField()
    image = models.ImageField(
        upload_to=upload_user_directory, null=True, blank=True)
    star1 = models.FloatField(null=False, default=0.0)
    star2 = models.FloatField(null=False, default=0.0)
    star3 = models.FloatField(null=False, default=0.0)
    star4 = models.FloatField(null=False, default=0.0)
    total_star = models.FloatField(null=False, default=0.0)
    like = models.ManyToManyField(User, related_name="review_like", blank=True)

    class Meta:
        ordering = ['-id']

    def like_count(self):
        return self.like.values().count()

    def __str__(self):
        if not self.post == None:
            category = "Post"
            title = self.post.title
        elif not self.autocamp == None:
            category = "Autocamp"
            title = self.autocamp.title
        elif not self.userpostinfo == None:
            category = "UserPostInfo"
            title = self.userpostinfo.user_post.title
        else:
            category = "Undefined Category"
            title = "Undefined Comment"

        return f"{category} | {title}"


class Comment(Base):
    user = models.ForeignKey(User, on_delete=CASCADE,
                             related_name="comment", null=False)
    ecocarping = models.ForeignKey(
        EcoCarping, on_delete=CASCADE, related_name="comment", null=True, blank=True)
    share = models.ForeignKey(Share, on_delete=CASCADE,
                              related_name="comment", null=True, blank=True)
    text = models.CharField(max_length=50)
    root = models.ForeignKey('self', related_name='root_comment',
                             on_delete=models.CASCADE, null=True, blank=True)
    like = models.ManyToManyField(
        User, related_name="comment_like", blank=True)

    def __str__(self):
        return '{} : {}'.format(self.user, self.text)
