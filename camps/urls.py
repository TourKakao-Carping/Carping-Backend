from django.urls import path, include
from camps.views import *
from camps.inputdata import InputDataAPIView

urlpatterns = [
    path('input-data', InputDataAPIView.as_view()),
    # path('popular-search', GetPopularSearchList.as_view())
]
