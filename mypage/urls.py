from django.urls import path
from rest_framework import routers

from mypage.views import MyPageView, ProfileUpdateViewSet, PostStatusView

urlpatterns = [
    path('sort', MyPageView.as_view(), name="mypage-sort"),
    path('post-status', PostStatusView.as_view(), name="user-post-status")
]

router = routers.DefaultRouter()
router.register('profile', ProfileUpdateViewSet)

urlpatterns += router.urls
