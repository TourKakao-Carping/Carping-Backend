from django.shortcuts import render
from rest_framework import viewsets

from posts.models import EcoCarping
from posts.serializers import EcoCarpingSerializer


class EcoCarpingViewSet(viewsets.ModelViewSet):
    serializer_class = EcoCarpingSerializer
    queryset = EcoCarping.objects.all()

