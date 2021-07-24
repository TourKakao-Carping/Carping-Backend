from django.urls import path, include
from accounts import views

urlpatterns = [
    path('login/kakao/',
         views.KakaoLoginView.as_view(), name='kakao_login'),
    path('login/google/',
         views.google_login_view, name='google_login'),
    path('kakao/social/', views.kakao_login, name='kakao_login'),
    path('kakao/callback/', views.kakao_callback, name='kakao_callback'),
    path("login/kakao/", views.KakaoLoginView.as_view(), name="kakao_social")
    # path('kakao/login/finish/', views.KakaoLoginView.as_view(), name='kakao_login'),
]
