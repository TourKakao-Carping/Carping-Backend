from django.urls import path, include
from rest_framework import routers

from camps.views import *
from camps.inputdata import InputDataAPIView
from camps.viewsets import AutoCampViewSet

urlpatterns = [
    path('input-data', InputDataAPIView.as_view()),
    # path('popular-search', GetPopularSearchList.as_view())
    path('auto-camp/partial', AutoCampPartial.as_view(), name='auto-camp-main'),
]

router = routers.DefaultRouter()
router.register('auto-camp', AutoCampViewSet)

urlpatterns += router.urls
