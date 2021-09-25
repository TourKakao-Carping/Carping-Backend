from rest_framework import routers
from django.urls import path, include

from posts.inputdata import InputRegionView
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
    # path('share/input-data', InputRegionView.as_view(), ),
    path('store', StoreListView.as_view(), name='store'),
    path('user-post', UserPostInfoListAPIView.as_view(),
         name="user-post-info-list"),
    path('user-post/info/<int:pk>/',
         UserPostInfoDetailAPIView.as_view(), name="user-post-info"),
    path('user-post/detail/<int:pk>',
         UserPostDetailAPIView.as_view(), name="user-post"),
]

router = routers.DefaultRouter()
router.register('eco-carping', EcoCarpingViewSet)
router.register('autocamp', AutoCampPostForWeekendViewSet)
router.register('share', ShareViewSet)

urlpatterns += router.urls
