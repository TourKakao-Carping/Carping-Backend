from django.urls import path

from mypage.views import MyPageView, MyProfileView, MyInfoView

urlpatterns = [
    path('sort', MyPageView.as_view(), name="mypage-sort"),
    path('profile', MyProfileView.as_view(), name="myinfo"),
    path('profile/info', MyInfoView.as_view(), name="myinfo"),
]
