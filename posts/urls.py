from rest_framework import routers
from django.urls import path, include
from posts.views import EcoCarpingViewSet, EcoRankingView

router = routers.DefaultRouter()
router.register('eco-carping', EcoCarpingViewSet)

urlpatterns = [
    path('eco-ranking', EcoRankingView.as_view(), name='eco-ranking')
]

urlpatterns += router.urls
