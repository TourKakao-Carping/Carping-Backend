from rest_framework import routers
from django.urls import path, include

from posts.inputdata import InputRegionView
from posts.viewsets import AutoCampPostForWeekendViewSet, EcoCarpingViewSet, ShareViewSet
from posts.views import *
from posts.callback import *

urlpatterns = [
    # path('region', InputRegionView.as_view(), name="input-region"),
    path('autocamp/weekend-post',
         GetAutoCampPostForWeekend.as_view(), name="weekend-post"),
    path('eco-carping/sort',
         EcoCarpingSort.as_view(), name="ecocarping-sort"),
    path('eco-carping/like', EcoLike.as_view(), name='eco-carping-like'),
    path('share/sort',
         ShareSort.as_view(), name="share-sort"),
    path('share/search',
         RegionSearchView.as_view(), name="share-region-search"),
    path('share/like', ShareLike.as_view(), name='share-like'),
    path('share/complete', ShareCompleteView.as_view(), name='share-complete'),
    # path('share/input-data', InputRegionView.as_view(), ),
    path('store', StoreListView.as_view(), name='store'),

    # 메인페이지 List (A부터 Z, 차박 포스트 페이지, 카테고리)
    path('user-post', UserPostInfoListAPIView.as_view(),
         name="user-post-info-list"),

    # 생성 API
    path('user-post/pre-create', PreUserPostCreateAPIView.as_view(),
         name="user-post-pre-create"),
    path('user-post/compute-fee', ComputeFeeView.as_view(),
         name="user-post-compute-fee"),
    path('user-post/create', UserPostCreateAPIView.as_view(),
         name="user-post-create"),

    # 삭제 API
    path('user-post/<int:pk>/deactivate',
         UserPostDeactivateAPIView.as_view(), name="user"),

    # 유저포스트 활성/비활성화 Admin API
    path('user-post/<int:pk>/<int:type>/admin',
         UserPostAdminActionAPIView.as_view(), name="admin-user-activate"),

    # 상세보기 API
    path('user-post/info/<int:pk>',
         UserPostInfoDetailAPIView.as_view(), name="user-post-info"),
    path('user-post/info/<int:pk>/free', FreeUserPostBuyAPIView.as_view(),
         name="free-user-post-buy"),
    path('user-post/info/<int:pk>/reviews',
         UserPostMoreReviewAPIView.as_view(), name="user-post-info"),
    path('user-post/<int:pk>',
         UserPostDetailAPIView.as_view(), name="user-post"),

    path('user-post/like', UserPostLike.as_view(), name='user-post-like'),

    # 결제 API
    path('user-post/<int:pk>/payment-ready',
         UserPostPaymentReadyAPIView.as_view(), name='kakao-pay-ready'),

    # 결제 콜백 API
    path('user-post/callback/<int:pk>/fail', UserPostFailCallbackAPIView.as_view(),
         name="user-post-fail-callback"),
    path('user-post/callback/<int:pk>/cancel', UserPostCancelCallbackAPIView.as_view(),
         name="user-post-cancel-callback"),
    path('user-post/callback/<int:pk>/success', UserPostSuccessCallbackAPIView.as_view(),
         name="user-post-cancel-callback"),
]

router = routers.DefaultRouter()
router.register('eco-carping', EcoCarpingViewSet)
router.register('autocamp', AutoCampPostForWeekendViewSet)
router.register('share', ShareViewSet)

urlpatterns += router.urls
