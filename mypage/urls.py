from django.urls import path
from rest_framework import routers

from mypage.views import MyPageView, ProfileUpdateViewSet, PostStatusView, ProfileView

urlpatterns = [
    path('sort', MyPageView.as_view(), name="mypage-sort"),
    path('post-status', PostStatusView.as_view(), name="user-post-status"),
    path('profile/<int:pk>', ProfileView.as_view(), name='profile-detail'),
    path('profile/<int:pk>/', ProfileUpdateViewSet.as_view(), name='profile-update')
]
