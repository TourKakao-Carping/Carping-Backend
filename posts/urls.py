from posts.views import *
from rest_framework import routers
from django.urls import path, include
from posts.views import EcoCarpingViewSet, EcoRankingView

urlpatterns = [
    path('autocamp/weekend-post',
         GetAutoCampPostForWeekend.as_view(), name="weekend-post"),
    path('eco-ranking', EcoRankingView.as_view(), name='eco-ranking')
]

router = routers.DefaultRouter()
router.register('eco-carping', EcoCarpingViewSet)

urlpatterns += router.urls
