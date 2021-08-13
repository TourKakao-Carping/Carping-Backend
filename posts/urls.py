from django.urls import path, include
from posts.views import *

urlpatterns = [
    path('autocamp/weekend-post', GetAutoCampPostForWeekend),
]
