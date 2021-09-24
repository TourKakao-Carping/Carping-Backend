from django.urls import path
from rest_framework import routers
from search.views import *

urlpatterns = [
    path('map', ToursiteSearchView.as_view(), name='map-search'),
    path('map/auto-camp', AutoCampMapView.as_view(), name='map-auto-camp'),
    path('region', RegionTourView.as_view(), name='region-popular-campsite'),
]

router = routers.DefaultRouter()

urlpatterns += router.urls
