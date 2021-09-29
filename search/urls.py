from django.urls import path
from rest_framework import routers
from search.views import *

urlpatterns = [
    path('main', MainSearchView.as_view(), name='main-search'),
    path('posts', UserPostSearchView.as_view(), name='user-post-search'),
    path('complete', KeywordSaveView.as_view(), name='search-complete'),
    path('keyword', UserKeywordView.as_view(), name='user-keyword'),
    path('map', ToursiteSearchView.as_view(), name='map-search'),
    path('map/auto-camp', AutoCampMapView.as_view(), name='map-auto-camp'),
    path('region', RegionTourView.as_view(), name='region-popular-campsite'),
]

router = routers.DefaultRouter()

urlpatterns += router.urls
