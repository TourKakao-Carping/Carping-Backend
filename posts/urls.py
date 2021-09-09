from rest_framework import routers
from django.urls import path, include

from posts.viewsets import AutoCampPostForWeekendViewSet, EcoCarpingViewSet, ShareViewSet
from posts.views import *

urlpatterns = [
    path('autocamp/weekend-post',
         GetAutoCampPostForWeekend.as_view(), name="weekend-post"),
    path('eco-carping/sort',
         EcoCarpingSort.as_view(), name="ecocarping-sort"),
    path('eco-carping/like', EcoLike.as_view(), name='eco-carping-like'),
    path('share/sort',
         ShareSort.as_view(), name="share-sort"),
    path('share/like', ShareLike.as_view(), name='share-like'),
    path('share/complete', ShareCompleteView.as_view(), name='share-complete'),
]

router = routers.DefaultRouter()
router.register('eco-carping', EcoCarpingViewSet)
router.register('autocamp', AutoCampPostForWeekendViewSet)
router.register('share', ShareViewSet)

urlpatterns += router.urls
