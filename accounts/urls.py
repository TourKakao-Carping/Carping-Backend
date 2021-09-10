from django.urls import path, include
from accounts import views, tokens

urlpatterns = [
    path('kakao/social', views.kakao_login, name='kakao_login'),
    path('kakao/callback', views.kakao_callback, name='kakao_callback'),

    path('google/social', views.google_login, name='google_login'),
    path('google/callback', views.google_callback, name='google_callback'),

    path("login/kakao", views.KakaoLoginView.as_view(), name="kakao_social"),
    path("login/google", views.GoogleLoginView.as_view(), name="google_social"),

    path("token/refresh", tokens.CustomTokenRefreshView.as_view(),
         name="token_refresh"),

    path('eco-ranking', views.EcoRankingView.as_view(), name='eco-ranking'),

    path('send-sms', views.SmsSendView.as_view(), name='send-sms'),
    path('sms-verification', views.SMSVerificationView.as_view(), name='sms-verification'),
]
