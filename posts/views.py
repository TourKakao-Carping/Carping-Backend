from django.shortcuts import render
from rest_framework.generics import GenericAPIView
from rest_framework.views import APIView
from rest_framework import viewsets

from posts.models import EcoCarping
from posts.serializers import EcoCarpingSerializer


class GetAutoCampPostForWeekend(GenericAPIView):
    def get_queryset(self):
        return super().get_queryset()


class EcoCarpingViewSet(viewsets.ModelViewSet):
    serializer_class = EcoCarpingSerializer
    queryset = EcoCarping.objects.all()
