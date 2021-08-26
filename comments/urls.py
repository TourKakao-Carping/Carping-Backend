from django.urls import path
from rest_framework import routers

from comments.views import ReviewLike, CommentLike
from comments.viewsets import ReviewViewSet, CommentViewSet

urlpatterns = [
    path('review/like', ReviewLike.as_view(), name='review-like'),
    path('comment/like', CommentLike.as_view(), name='comment-like')
]

router = routers.DefaultRouter()
router.register('review', ReviewViewSet)
router.register('comment', CommentViewSet)

urlpatterns += router.urls
