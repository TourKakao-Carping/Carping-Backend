from django.urls import path
from rest_framework import routers

from comments.views import ReviewLike
from comments.viewsets import ReviewViewSet

urlpatterns = [
    path('review/like', ReviewLike.as_view(), name='review-like')
]

router = routers.DefaultRouter()
router.register('review', ReviewViewSet)

urlpatterns += router.urls
