from rest_framework import viewsets
from rest_framework.mixins import RetrieveModelMixin, UpdateModelMixin, DestroyModelMixin, CreateModelMixin
from rest_framework.viewsets import GenericViewSet

from posts.serializers import AutoCampPostSerializer, EcoCarpingSerializer
from posts.models import EcoCarping, Post
from bases.response import APIResponse
from rest_framework.exceptions import MethodNotAllowed


# 4. 실시간 에코리뷰 api - 최근 3개 (사진, 제목, 내용, 시간, 리뷰날짜, pk, 오늘에코리뷰 인증 수 )
class EcoCarpingViewSet(RetrieveModelMixin, UpdateModelMixin, DestroyModelMixin, CreateModelMixin, GenericViewSet):
    serializer_class = EcoCarpingSerializer
    queryset = EcoCarping.objects.all()

    def retrieve(self, request, *args, **kwargs):
        response = APIResponse(False, '')
        try:
            ret = super(EcoCarpingViewSet, self).retrieve(request)
            response.success = True
            return response.response(data=[ret.data], status=200)
        except Exception as e:
            response.code = "NOT_FOUND"
            return response.response(data=str(e), status=404)

    def create(self, request, *args, **kwargs):
        response = APIResponse(False, '')
        ret = super(EcoCarpingViewSet, self).create(request)
        response.success = True
        return response.response(data=[ret.data], status=200)


class AutoCampPostForWeekendViewSet(viewsets.ModelViewSet):
    """
    이번주말 이런차박지 어때요 상세페이지 가져오기 API
    """
    serializer_class = AutoCampPostSerializer
    queryset = Post.objects.all().order_by('-created_at')

    http_method_names = ['get', ]

    def list(self, request, *args, **kwargs):
        raise MethodNotAllowed("GET")

    def retrieve(self, request, *args, **kwargs):
        response = APIResponse(False, '')
        try:
            ret = super(AutoCampPostForWeekendViewSet, self).retrieve(request)

            response.success = True
            return response.response(data=[ret.data], status=200)
        except Exception as e:
            response.code = "NOT_FOUND"
            return response.response(data=str(e), status=404)
