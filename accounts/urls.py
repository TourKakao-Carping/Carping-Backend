from django.urls import path, include
from accounts import views

urlpatterns = [
    path('login/kakao/',
         views.KakaoLoginView.as_view(), name='kakao_login'),
    path('login/google/',
         views.google_login_view, name='google_login'),
]
