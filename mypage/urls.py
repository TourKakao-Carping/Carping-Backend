from django.urls import path

from mypage.views import MyPageView, MyInfoView

urlpatterns = [
    path('sort', MyPageView.as_view(), name="mypage-sort"),
    path('profile/info', MyInfoView.as_view(), name="myinfo"),
]
