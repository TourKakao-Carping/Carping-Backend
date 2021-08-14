from django.urls import path, include
from camps.views import *

urlpatterns = [
    # path('input-data', InputDataAPIView.as_view()),
    path('popular-search', GetPopularSearchList.as_view())
]
