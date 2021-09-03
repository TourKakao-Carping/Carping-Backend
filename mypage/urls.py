from django.urls import path, include

from mypage.views import MyPageView

urlpatterns = [
    path('sort', MyPageView.as_view(), name="mypage-sort"),
]
