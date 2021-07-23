from django.urls import path, include
from accounts import views

urlpatterns = [
    path('kakao/login/',
         views.KakaoLoginView.as_view(), name='kakao_login'),
]
