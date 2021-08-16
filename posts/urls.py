from rest_framework import routers
from django.urls import path, include

from posts.viewsets import AutoCampPostForWeekendViewSet, EcoCarpingViewSet
from posts.views import *

urlpatterns = [
    path('autocamp/weekend-post',
         GetAutoCampPostForWeekend.as_view(), name="weekend-post"),
    path('eco-carping/partial',
         EcoCarpingPartial.as_view(), name="partial-ecocarping"),
]

router = routers.DefaultRouter()
router.register('eco-carping', EcoCarpingViewSet)
router.register('autocamp', AutoCampPostForWeekendViewSet)

urlpatterns += router.urls
