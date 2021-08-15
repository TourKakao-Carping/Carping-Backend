from camps.models import AutoCamp
from rest_framework import viewsets
from posts.serializers import AutoCampPostSerializer, EcoCarpingSerializer
from posts.models import EcoCarping, Post
from bases.response import APIResponse
from rest_framework.response import Response


class EcoCarpingViewSet(viewsets.ModelViewSet):
    serializer_class = EcoCarpingSerializer
    queryset = EcoCarping.objects.all()


class AutoCampPostForWeekendViewSet(viewsets.ModelViewSet):
    serializer_class = AutoCampPostSerializer
    queryset = Post.objects.all().order_by('-created_at')

    def list(self, request, *args, **kwargs):
        response = APIResponse(False, '')
        try:
            ret = super(AutoCampPostForWeekendViewSet, self).list(request)

            response.success = True
            return response.response(data=ret.data, status=200)
        except Exception as e:
            response.code = "EXCEPTION_ERROR"
            return response.response(data=e, status=500)

    def retrieve(self, request, *args, **kwargs):
        response = APIResponse(False, '')
        try:
            ret = super(AutoCampPostForWeekendViewSet, self).retrieve(request)

            response.success = True
            return response.response(data=ret.data, status=200)
        except Exception as e:
            response.code = "EXCEPTION_ERROR"
            return response.response(data=e, status=500)
