from django.urls import path
from rest_framework import routers

from mypage.views import MyPageView, ProfileUpdateViewSet

urlpatterns = [
    path('sort', MyPageView.as_view(), name="mypage-sort"),
]

router = routers.DefaultRouter()
router.register('profile', ProfileUpdateViewSet)

urlpatterns += router.urls
