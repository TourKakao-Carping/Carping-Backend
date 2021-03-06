from django.urls import path, include
from rest_framework import routers

from camps.views import *
from camps.inputdata import InputDataAPIView, InputTagAPIView, InputTourAPIView, InputTourAddressAPIView
from camps.viewsets import AutoCampViewSet


urlpatterns = [
    #     path('input-data', InputDataAPIView.as_view()),
    # path('input-tags', InputTagAPIView.as_view()),
    # path('popular-search', GetPopularSearchList.as_view()),
    # path('input-tour', InputTourAPIView.as_view()),
    # path('input-tour-address', InputTourAddressAPIView.as_view()),
    path('auto-camp/partial', AutoCampPartial.as_view(), name='auto-camp-main'),
    path('auto-camp/bookmark', AutoCampBookMark.as_view(),
         name='auto-camp-bookmark'),
    path('theme/bookmark', CampSiteBookMark.as_view(),
         name='campsite-bookmark'),
    path('theme', GetMainPageThemeTravel.as_view(), name='mainpage-theme'),
    path('theme/detail/<int:pk>',
         CampSiteDetailAPIView.as_view(), name='theme-detail')
]

router = routers.DefaultRouter()
router.register('auto-camp', AutoCampViewSet)

urlpatterns += router.urls
