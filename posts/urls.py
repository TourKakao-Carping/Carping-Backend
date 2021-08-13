from django.urls import path, include
from posts.views import *
from rest_framework import routers
from django.urls import path, include
from posts.views import EcoCarpingViewSet

urlpatterns = [
    path('autocamp/weekend-post', GetAutoCampPostForWeekend),
]

router = routers.DefaultRouter()
router.register('eco-carping', EcoCarpingViewSet)

urlpatterns = router.urls
